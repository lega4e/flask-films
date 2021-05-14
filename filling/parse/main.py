#!/usr/bin/python3
############################################################
# import
import asyncio as aio
import os
import re
import parse_rating_page
import parse_work_page

from aiohttp    import ClientSession
from pageloader import LoadPageTask, PageLoader
from nvxlira    import Lira
from nvxaex     import Executor
from nvxiex     import IntervalExecutor
from threading  import Thread 
from nvxstruct  import struct





############################################################
# functions
def generate_rating_pages():
	film_template = 'http://www.world-art.ru/cinema/rating_top.php?limit_1=%i&&limit_2=%i'
	tv_template   = 'http://www.world-art.ru/cinema/rating_tv_top.php?limit_1=%i&public_list_anchor=%i'
	end = [ 0, 601, 201, 101, 301 ]

	for i in range(1, 7102, 50):
		yield film_template % (i, i + 49)

	for i in range(1, 5):
		for limit in range(0, end[i], 50):
			yield tv_template % (limit, i)
	
	return





############################################################
# class
class ParseTask:
	def __init__(self, filename):
		self.filename = filename
		self.done = False

	def __str__(self):
		return self.filename

class LoadPageTask(LoadPageTask):
	def __str__(self):
		return self.filename





############################################################
# functions
def add_parse_rating_task(task, html):
	lira.put(ParseTask(task.filename), cat='rtpgpr')
	return

async def parse_rtpg(task):
	try:
		for obj in parse_rating_page.parse(task):
			newtask = LoadPageTask(
				obj.url,
				'works/' + re.search('id=(\d+)', obj.url).group(1) + '.html'
			)
			newtask.bscore = obj.bscore
			newtask.year   = obj.year
			newtask.score  = obj.score
			newtask.voted  = obj.voted
			id = lira.put(newtask, cat='load-wkpg')
	except Exception as e:
		print(e)
	return True


def add_parse_work_task(task, html):
	try:
		newtask = ParseTask(task.filename)
		newtask.bscore = task.bscore
		newtask.year   = task.year
		newtask.score  = task.score
		newtask.voted  = task.voted
		lira.put(newtask, cat='wkpgpr')
	except Exception as e:
		print(e)

async def parse_wkpg(task):
	try:
		obj = parse_work_page.parse(task)
		lira.put(obj, cat='work')
	except Exception as e:
		print('on %s :' % task.filename, e)
	return True





############################################################
# main
lira = Lira('data.bin', 'head.bin')
ex = Executor(lira, None, silent=False)

async def rtpgld():
	global ex
	async with ClientSession() as session:
		rtpgloader = PageLoader(session, callback=add_parse_rating_task)
		ex.fun = rtpgloader
		ex.workerc = 15
		await ex.extasks('load-rtpg', 'load-rtpg-done')

async def wkpgld():
	try:
		global ex
		async with ClientSession() as session:
			wkpgloader = PageLoader(session, callback=add_parse_work_task)
			ex.fun = wkpgloader
			ex.workerc = 15
			await ex.extasks('load-wkpg', 'load-wkpg-done')
	except Exception as e:
		print(e)


async def rtpgpr():
	global ex
	ex.fun = parse_rtpg
	ex.workerc = 1
	await ex.extasks('rtpgpr', 'rtpgpr-done')


async def wkpgpr():
	global ex
	ex.fun = parse_wkpg
	ex.workerc = 1
	await ex.extasks('wkpgpr', 'wkpgpr-done')





############################################################
# ex

try: os.mkdir('rating')
except: pass

try: os.mkdir('works')
except: pass


th = Thread(target=lambda: aio.run(wkpgpr()))
th.start()
#  th.join()





############################################################
# other
print(len(lira['rtpgpr']))
print(len(lira['rtpgpr-done']))
print(len(lira['load-wkpg']))
print(len(lira['load-wkpg-done']))
print(len(lira['wkpgpr']))
print(len(lira['wkpgpr-done']))
print(len(lira['work']))

print(len(os.listdir('works')))
for filename in os.listdir('works'):
	print(filename)

print(max([ len(lira.get(id).ann) if lira.get(id).ann else 0 for id in lira['work'] ]))
max(map(lambda tag: len(tag.desc), reduce(lambda a, b: a + b, [ lira.get(id).tag for id in lira['work'] ])))


for filename in os.listdir('rating'):
	lira.put(ParseTask('rating/' + filename), cat='rtpgpr')

for id in lira['rtpgpr-done']:
	lira.out(id)

for id in lira['load-wkpg']:
	task = lira.get(id)
	lira.out(id)
	newtask = ParseTask(task.filename)
	newtask.bscore = task.bscore
	newtask.year   = task.year
	newtask.score  = task.score
	newtask.voted  = task.voted
	lira.put(newtask, cat='wkpgpr')

for id in lira['work'][::1000]:
	work = lira.get(id)
	print(work.prettify())

iex = IntervalExecutor(lambda: lira.flush(), 5.0)
iex.start()
iex.stop()





# END
