import asyncio as aio
import os
import re

from aiohttp    import ClientSession
from pageloader import LoadPageTask, PageLoader
from nvxlira    import Lira
from nvxaex     import Executor





############################################################
# class	
class LoadPage(LoadPageTask):
	def __str__(self):
		return self.filename





############################################################
# lira
lira = Lira('data.bin', 'head.bin')

if len(lira['load-page']) == 0 and len(lira['load-page-done']) == 0:
	for url in [
		'http://www.world-art.ru/cinema/cinema.php?id=65021',
		'http://www.world-art.ru/cinema/cinema.php?id=17190',
		'http://www.world-art.ru/cinema/cinema.php?id=36896',
		'http://www.world-art.ru/cinema/cinema.php?id=547',
		'http://www.world-art.ru/cinema/cinema.php?id=50952'
	]:
		task = LoadPage(url=url, filename='works/' + re.search('id=(\d+)', url).group(1) + '.html')
		lira.put(task, cat='load-page')

print('Not done:')
for task in [ lira.get(id) for id in lira['load-page'] ]:
	print(task)

print('Done:')
for task in [ lira.get(id) for id in lira['load-page-done'] ]:
	print(task)





############################################################
# main
async def main():
	async with ClientSession() as session:
		loader = PageLoader(session, silent=False)
		ex = Executor(lira, loader, silent=False)
		await ex.extasks('load-page', 'load-page-done')
	return





############################################################
# run
try: os.mkdir('works')
except: pass

aio.run(main())




del lira
############################################################
# END
