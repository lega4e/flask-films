# 
# Инициализация модуля, отвечающего за работу
# с базой данных; 
#
############################################################
# import
import random

from sqlalchemy     import func
from sqlalchemy.orm import sessionmaker
from app.bd.table   import *
from nvxsct         import sct





############################################################
# prepare
Base.metadata.create_all(engine)
Session = sessionmaker(engine)
session = Session()

work_count = session.query(Work).count()
types     = sorted([ c[0] for c in session.query(Work.atype).distinct(Work.atype)           ])
countries = sorted([ c[0] for c in session.query(Country.country).distinct(Country.country) ])
genres    = sorted([ c[0] for c in session.query(Genre.genre).distinct(Genre.genre)         ])
tags      = sorted([ c[0] for c in session.query(Tag.tag).distinct(Tag.tag)                 ])
minyear = session.query(func.min(Work.year)).one()[0]
maxyear = session.query(func.max(Work.year)).one()[0]





############################################################
# functions
query_maxlen = 10
last_queries = [] # [ sct(token : str, query, sets, count) ]

def generate_token():
	'''
	Генерирует случайную строку из трёх символов
	(цифры и строчные латинские буквы), которой не
	содержится в last_queries; эта строка и есть токен
	'''
	token = ''
	while token == '' or len([ s for s in last_queries if s.token == token]) != 0:
		token = ''
		for i in range(3):
			token += random.choice('0123456789abcdefghijklmnopqrstuvwxyz')
	return token


def get_rating(sets, token=None):
	'''
	Есть несколько вариантов использования:

	Во-первых, передать sets (настройки поиска) без токена: в этом
	случае будет сформирован и сохранён соответствующий запрос;
	возвращены будут не только соответствующие произведения,
	но и дополнительная структура, содержащая следующие поля:

	struct:
	  token (три уникальных символа, идентифицирующие запрос)
	  query (объект запроса; не использовать вне этого модуля)
	  sets  (настройки запроса)
	  count (количество найденных работ по данному запросу)

	Во-вторых, передать ещё и токен: будут извлечена сохранённая
	структура (см. выше) и отданы соответствующие работы вместе
	со структурой. Если структуры с таким токеном не существует,
	то запрос будет сведён к первому варианту
	'''
	extra = sct(token=token, query=None, sets=sets, count=0) # структура


	# Вариант с токеном
	if token:
		extra = [ extra for extra in last_queries if extra.token == token ]
		if len(extra) == 0:
			print('Expired token')
			extra.token = None
		else:
			extra = extra[0]


	# Если токена нет или он просрочен
	if not extra.token:
		extra.query = session.query(Work)

		# Формирование запроса в соответствии с настройками
		if sets.atype != 'Не выбрано':
			extra.query = extra.query.filter_by(atype=sets.atype)

		if sets.genre != 'Не выбрано':
			extra.query = extra.query.join(WorkGenre).join(Genre).filter(Genre.genre == sets.genre)

		if sets.country != 'Не выбрано':
			extra.query = extra.query.join(WorkCountry).join(Country).filter(Country.country == sets.country)

		if sets.tag != 'Не выбрано':
			extra.query = extra.query.join(WorkTag).join(Tag).filter(Tag.tag == sets.tag)

		if sets.minyear:
			extra.query = extra.query.filter(Work.year >= sets.minyear)

		if sets.maxyear:
			extra.query = extra.query.filter(Work.year <= sets.maxyear)

		if sets.base != 'Не выбрано':
			extra.query = extra.query.filter(Work.base == sets.base)

		if sets.director != 'Не выбрано':
			extra.query = extra.query.join(Director).filter(Director.director == sets.director)

		if sets.idea != 'Не выбрано':
			extra.query = extra.query.join(Idea).filter(Idea.idea == sets.idea)

		if sets.actor != 'Не выбрано':
			extra.query = extra.query.join(WorkActor).join(Actor).filter(Actor.actor == sets.actor)

		if sets.like != None:
			extra.query = extra.query.filter(Work.name.like('%' + sets.like + '%'))

		extra.query = extra.query.order_by( *{
			'По расчётному баллу (возр.)'   : [ Work.bscore                           ],
			'По расчётному баллу (убыв.)'   : [ Work.bscore.desc()                    ],
			'По среднему баллу (возр.)'     : [ Work.score,        Work.bscore        ],
			'По среднему баллу (убыв.)'     : [ Work.score.desc(), Work.bscore.desc() ],
			'По году (возр.)'               : [ Work.year,         Work.bscore.desc() ],
			'По году (убыв.)'               : [ Work.year.desc(),  Work.bscore.desc() ],
			'По названию (возр.)'           : [ Work.name,         Work.bscore.desc() ],
			'По названию (убыв.)'           : [ Work.name.desc(),  Work.bscore.desc() ],
			'По количеству голосов (возр.)' : [ Work.voted,        Work.bscore.desc() ],
			'По количеству голосов (убыв.)' : [ Work.voted.desc(), Work.bscore.desc() ],
		}[sets.sorting] )

		# Установка полей структуры с дополнительными данными
		extra.token = generate_token()
		extra.count = extra.query.count()

		last_queries.append(extra)
		if len(last_queries) > query_maxlen:
			del last_queries[0]


	# Получение результата и нумерация
	res = extra.query[sets.offset:sets.offset+sets.limit]
	for i in range(len(res)):
		res[i].num = i + sets.offset + 1

	return res, extra


def get_work(id):
	return session.query(Work).filter_by(work_id=id).one()


def create_sets_struct():
	'''
	Вспомогательная функция, которая создаёт
	настройки запроса "по умолчанию"
	'''
	return sct(
		atype    = 'Не выбрано',
		genre    = 'Не выбрано',
		country  = 'Не выбрано',
		tag      = 'Не выбрано',
		minyear  = minyear,
		maxyear  = maxyear,
		base     = 'Не выбрано',
		director = 'Не выбрано',
		idea     = 'Не выбрано',
		actor    = 'Не выбрано',
		sorting  = 'По расчётному баллу (убыв.)',
		offset   = 0,
		limit    = 50,
		like     = None
	)





############################################################
# END
