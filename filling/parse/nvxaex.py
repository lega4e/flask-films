import aiohttp
import datetime as dt

from asyncio   import CancelledError, Queue, create_task, gather
from nvxlira   import Lira
from threading import Lock





class NoneTaskException(Exception):
	def __init__(self, id):
		self.id = id

	def __str__(self):
		return 'Exception: Task is None (id: %s)' % str(self.id)



class Executor:
	'''
	Executor — класс, предназначенный для выполнения
	множества задач, которые берутся из Лиры и кладутся
	после успешного выполнения туда же. Для корректной
	работы необходимо установить следующие члены:

	lira - объект lira, откуда берутся задачи и куда
	       кладутся
	fun  - функция, которая выполняет задачу и возвращает
	       True в случае успеха и False — иначе; если 
	       используются асинхронные методы, то и эта
		   функция должна быть асинхронной 
	
	Дополнительно можно установить следующие члены:

	name    - имя исполнителя (используются в сообщениях
	          о работе, если silent = False)
	silent  - флаг, который указывает, нужно ли выводить
	          сообщения о работе
	workerc - количество работников (по умолчанию 5), 
	          которые будут выполнять задания из очереди
			  (используется только в методе extasks)

	Заданием может выступать любой объект, который
	имеет булевый член done
	'''

	def __init__(
		self, lira : Lira, fun,
		name    = 'Ex',
		silent  = True,
		workerc = 5
	):
		self.lira     = lira
		self.fun      = fun
		self.name     = name
		self.silent   = silent
		self.workerc  = workerc
		self.stopflag = False
		self.stoplock = Lock()
		self.taskc    = None   # task count
		self.compc    = None   # complete task count
		self.btime    = None
		self.que      = Queue()
		self.workers  = []
		pass



	def stop(self):
		'Останавливает выполнение задач'
		with self.stoplock:
			self.stopflag = True
		for w in self.workers:
			w.cancel()
		return



	def stopped(self):
		'Проверяет, остановлено ли выполнение задач'
		with self.stoplock:
			res = self.stopflag
		return res



	def ex(self, id, outcat) -> bool:
		'Выполняет задачу id и сообщает об успехе'
		task = self.lira.get(id)
		if task is None:
			raise NoneTaskException(id)

		if task.done:
			return True

		result = self.fun(task)
		if not result:
			self._print_task_message(task, False)
			return False

		task.done = True
		self.lira.put(task, id, cat=outcat)
		if self.compc is not None:
			self.compc += 1
		self._print_task_message(task, True)
		return True



	async def ex_async(self, id, outcat) -> bool:
		'''
		Выполняет задачу id и сообщает об успехе
		(асинхронная версия)
		'''
		task = self.lira.get(id)
		if task is None:
			raise NoneTaskException(id)

		if task.done:
			return True

		try: result = await self.fun(task)
		except CancelledError as e: raise e
		except Exception as e: print(e); raise e

		if not result:
			self._print_task_message(task, False)
			return False

		task.done = True
		self.lira.put(task, id, cat=outcat)
		if self.compc is not None:
			self.compc += 1
		self._print_task_message(task, True)
		return True



	async def exque(self, outcat):
		try:
			while not self.stopped():
				try:
					id = await self.que.get()
					await self.ex_async(id, outcat)
					self.que.task_done()
				except CancelledError:
					if not self.stopped():
						return
					self.que.task_done()

			while not self.que.empty():
				self.que.get_nowait()
				self.que.task_done()
		except Exception as e:
			print(e)

		return



	async def extasks(self, cat, outcat):
		'''
		Формирует очередь из задач указанной
		категории (берутся все объекты из lira)
		и исполняет в асинхронном режиме
		'''
		if not self.silent:
			print('\n(%s) BEGIN\n' % self.name, flush=True)

		# Формирование очереди
		self.que = Queue()

		objs = self.lira[cat]
		if len(objs) != 0:
			for id in objs:
				self.que.put_nowait(id)
			self.taskc = self.que.qsize()
			self.compc = 0
			self.btime = dt.datetime.now()

			# Создание работников
			with self.stoplock:
				self.stopflag = False

			self.workers = [
				create_task(self.exque(outcat))
				for _ in range(self.workerc)
			]

			# Окончание работы
			await self.que.join()
			for w in self.workers:
				w.cancel()

			await gather(*self.workers)
			self.taskc = None
			self.compc = None
			self.btime  = None

		if not self.silent:
			print('\n(%s) END\n' % self.name, flush=True)

		return



	def run_que(self, outcat):
		self.workers = [
			create_task(self.exque(self.que, outcat))
			for _ in range(self.workerc)
		]
		return

	def put(self, task):
		id = self.lira.put(task)
		self.que.put_nowait(id)
		return

	def putid(self, id):
		self.que.put_nowait(id)
		return

	async def stop_que(self):
		for w in self.workers:
			w.cancel()
		await gather(*self.workers)
		return

	async def join_que(self):
		await self.que.join()
		await self.stop_que()
		return



	def _print_task_message(self, task, done):
		if self.silent:
			return
		done = 'Done:' if done else 'Fail:'
		try:
			if self.taskc is not None and self.btime is not None:
				delta = (dt.datetime.now() - self.btime).total_seconds()
				speed = self.compc / delta
				still = (self.taskc - self.compc) / speed
				print(
					'(%s | %6.2f%% : %5.1fs) %s %s' %
					(self.name, 100 * self.compc / self.taskc, still, done, str(task))
				)
			else:
				print('(%s) %s %s' % (self.name, done, str(task)))
		except Exception as e:
			print(e)
		return





# END
