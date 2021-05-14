import time

from threading import Thread, Lock





class IntervalExecutor(Thread):
	'''
	IntervalExecutor — это класс, который предназначен
	для интервального повторения какого-либо действия

	Уязвимость: время выполнения функции никак не 
	измеряется, поэтому, если эта функция будет выполняться
	значительное время, то фактический интервал выполнения
	будет больше заданного
	'''
	def __init__(self, fun, inter, delay = 0, checkinter = 0.001):
		'''
		fun        — функция, которая будет интервально выполняться
		inter      — интервал повторения (в секундах)
		delay      — задержка перед первым повторением
		checkinter — интервал с которым будет проверяться, что пора
		             выполнять функию
		'''
		Thread.__init__(self)
		self.fun        = fun
		self.inter      = inter
		self.delay      = delay
		self.checkinter = checkinter
		self.stoplock   = Lock()
		self.stopflag   = False

	def stop(self):
		with self.stoplock:
			self.stopflag = True
		return self

	def stoped(self) -> bool:
		with self.stoplock:
			res = self.stopflag
		return res

	def run(self):
		count = int(self.delay / self.checkinter)
		while not self.stoped():
			if count <= 0:
				self.fun()
				count = int(self.inter / self.checkinter)
			count -= 1
			time.sleep(self.checkinter)
		return





# END
