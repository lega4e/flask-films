import re

from bs4    import BeautifulSoup
from nvxsct import struct





# functions
def parse(task) -> struct:
	'''
	struct:
		work:
			name
			year
			atype
			dur
			epsc
			base
			score
			bscore
			voted
			imgref
			ann
		country:
			country
			order
		genre    : [ str ]
		director : str
		idea     : str
		actor    : [ struct: actor, order ]
		tag      : [ struct: tag, score, desc ]
	'''


	# create struct
	obj = struct(
		work = struct(
			year   = task.year,
			score  = task.score,
			bscore = task.bscore,
			voted  = task.voted
		)
	)

	fields = {
		'work.atype' : struct(hint='Формат',         tr=null),
		'work.dur'   : struct(hint='Хронометраж',    tr=dur_parse),
		'work.epsc'  : struct(hint='Кол-во серий',   tr=epsc_parse),
		'work.base'  : struct(hint='Основа',         tr=null),
		'country'    : struct(hint='Производство',   tr=country_parse),
		'genre'      : struct(hint='Жанр',           tr=genre_parse),
		'director'   : struct(hint='Режиссёр',       tr=director_parse),
		'idea'       : struct(hint='Автор идеи',     tr=idea_parse),
		'idea'       : struct(hint='Сценарий, идея', tr=director_parse),
		'actor'      : struct(hint='В ролях',        tr=actor_parse),
	}

	with open(task.filename, 'r') as file:
		text = file.read()
	soup = BeautifulSoup(text, 'lxml')


	# get name
	namesoup = soup.find(
		lambda tag:
			tag.name == 'font' and
			tag.has_attr('size') and
			tag['size'] == '5'
	)

	if namesoup is None:
		return None

	obj.work.name = namesoup.text


	# table soup
	table = (
		soup.body.center.find_all('table')[6].
		tr.td.table.tr.contents[4].
		find_all('table')[1].tr
	)


	# get imgref
	obj.work.imgref = 'http://www.world-art.ru/cinema/' + table.find('img')['src']


	# get fields
	for f in fields:
		tag = table.find(lambda tag:
			re.match(fields[f].hint, tag.text) is not None and
			tag.b is not None and 
			tag.b.text.startswith(fields[f].hint)
		)
		if tag is None:
			if f not in obj.__dict__:
				obj[f] = None
		else:
			obj[f] = fields[f].tr(tag.find_all('td')[2].text.strip(), obj)


	# tags
	obj.tag = []
	for tag in soup.select('.newtag'):
		obj.tag.append( struct(
			tag   = tag.a.text,
			score = float(tag.font.text) if tag.font else 3.0,
			desc  = tag.a['title']
		) )


	# annotation
	try:
		obj.work.ann = (
			soup.center.find_all('table')[6].
			tr.td.table.tr.contents[4].find(lambda tag:
				tag.name == 'table' and
				re.match('Краткое содержание', tag.text)
			)
		)
		if obj.work.ann is not None:
			obj.work.ann = obj.work.ann.next_sibling.p.text
	except Exception as e:
		print(e)


	return obj




# help parse functions
def nsib(tag, c):
	for i in range(c):
		tag = tag.next_sibling
	return tag



def null(a, obj):
	return a



def dur_parse(dur : str, obj) -> int:
	return epsc_parse(dur, obj)



def epsc_parse(epsc : str, obj) -> int:
	match = re.search(r'[^\d]*(\d+)[^\d]*', epsc)
	if match is None:
		return None
	return int(match.group(1))



def country_parse(countries : str, obj) -> [ struct ]:
	countries = list(map(lambda s: s.strip(), countries.split(', ')))
	res = []
	for i in range(len(countries)):
		res.append(struct(country=countries[i], order=i+1))
	return res



def genre_parse(genres : str, obj) -> [ str ]:
	return list(set(map(lambda s: s.strip(), genres.split(', '))))



def director_parse(director : str, obj) -> str:
	s = director.split(',')[0]
	pos = s.find('и другие')
	if pos < 0:
		return s.strip()
	return s[:pos].strip()



def idea_parse(idea : str, obj) -> str:
	base = re.search(r'\(([\w]+)\)', idea)
	if base is not None:
		obj.work.base = base.group(1)
	idea = idea[:idea.find('(')].strip()
	return idea



def actor_parse(actor : str, obj) -> [ str ]:
	actors = list(map(
		lambda s: struct(actor=s.country, order=s.order),
		country_parse(actor, obj)
	))
	if len(actors) == 0:
		return actors
	pos = actors[-1].actor.find('и другие')
	if pos >= 0:
		actors[-1].actor = actors[-1].actor[:pos].strip()
	return actors





# end
