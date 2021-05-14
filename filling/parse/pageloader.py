from asyncio import sleep
from random  import uniform
from nvxlira import Lira





class LoadPageTask:
	'''
	Задача по скачиванию http-страницы
	'''
	def __init__(self, url, filename, repeatc=64):
		'''
		url      — url страницы, которую нужно скачать
		filename — имя файла, куда нужно сохранить скачанную страницу
		repeatc  — количество попыток скачать страницу (при очень
		           частом обращении к серверу он может возвращать
				   страницу ошибки)
		'''
		self.url      = url
		self.filename = filename
		self.repeatc  = repeatc
		self.done     = False
		return

	def __repr__(self):
		return '%s -> %s' % ( self.url, self.filename )

	def __str__(self):
		return '%s -> %s' % ( self.url, self.filename )





class PageLoader:
	'''
	session  — объект aiohttp.ClientSession()
	silent   — флаг, указывающий, выводить ли сообщения об ошибке
	is_error — функция, которая будет проверять, является ли полученная
	           страница страницей ошибки (если не указана, будет
			   использоваться функция по умолчанию)
	callback — функция, которая будет вызываться при каждом успешном
	           считывании файла; в эту функцию первым аргументом будет
			   передаваться объект задания, а вторым — текст файла
	'''
	def __init__(self, session, silent=True, is_error=None, callback=None):
		self.session  = session
		self.silent   = silent
		self.is_error = is_error if is_error is not None else self._is_error
		self.callback = callback
		return

	async def __call__(self, task : LoadPageTask) -> bool:
		for _ in range(task.repeatc):
			await sleep(uniform(0.0, 1.0))
			async with self.session.get(task.url) as req:
				html = await req.text()
			if not self.is_error(html):
				break
			if not self.silent:
				print('Error: %s' % task.filename, flush=True)

		if self.is_error(html):
			return False

		with open(task.filename, 'w') as file:
			file.write(html)

		if self.callback is not None:
			self.callback(task, html)

		return True

	@staticmethod
	def _is_error(html):
		'Проверка по умолчанию, является ли полученная страница страницей ошибки'
		return len(html) < 5000





# END
