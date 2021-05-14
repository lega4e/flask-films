import re

from bs4 import BeautifulSoup
from nvxstruct import struct





def parse(task) -> [ struct ]:
	'Парсит отдельную страницу рейтинга'
	rating = []

	with open(task.filename, 'r') as file:
		text = file.read()

	soup = BeautifulSoup(text, 'lxml')

	lines = (
		soup.body.center.find_all('table')[6].
		tr.contents[2].
		center.table.td.find_all('table')[1].
		find_all('tr')[1:]
	)

	try:
		for line in lines:
			one        = struct()
			one.url    = 'http://www.world-art.ru/cinema/' + line.a['href']
			one.year   = int( re.search(r'\[(\d+)\]', line.contents[1].text).group(1) )
			one.voted  = int(line.contents[3].text)
			one.bscore = float(line.contents[2].text)
			one.score  = float(line.contents[4].text)
			rating.append(one)
	except:
		pass

	return rating





# END
