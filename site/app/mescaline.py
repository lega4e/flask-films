#
# Содержит разные вспомогательные функции
# 
import app.bd as bd

from nvxsct import sct





def generate_search_hint(sets):
	'''
	Создаёт строку, поясняющую выбранные настройки поиска
	'''
	s = []
	for label, value in [
		('Тип:',        sets.atype),
		('Жанр:',       sets.genre),
		('Год:',        (sets.minyear, sets.maxyear)),
		('Страна:',     sets.country),
		('Тег:',        sets.tag),
		('Основа:',     sets.base),
		('Режиссёр:',   sets.director),
		('Автор идеи:', sets.idea),
		('Актёр:',      sets.actor),
		('Сортировка:', sets.sorting),
	]:
		if label == 'Год:':
			if (
				value[0] is not None and value[1] is not None and
				(value[0] > bd.minyear or value[1] < bd.maxyear)
			):
				s.append('Год от %i до %i' % (value[0], value[1]))
		elif value != 'Не выбрано':
			s.append(label + ' ' + value)
	return ', '.join(s)



def create_page_struct(limit, page, iscur, token):
	if page == '...':
		return sct(type = '...')
	return sct(
		type   = 'page',
		offset = limit*(page - 1),
		limit  = limit,
		num    = page,
		iscur  = iscur,
		token  = token
	)



def generate_page_list(count, offset, limit, token) -> [ sct ]:
	'''
	Генерирует список страниц, в которые можно перейти
	из данной, т.е. это:

	1 ... 8 9 10 11 12 13 14 ... 143
	1 2 3 4 ... 143
	'''
	pagec    = (count - 1) // limit + 1
	curpage  = offset // limit + 1 # начиная с 1

	pages = {
		page for page in (list(range(curpage-3, curpage+4)) + [1, pagec])
		if page > 0 and page <= pagec
	} 

	if 3 in pages:
		pages.add(2)
	
	if pagec-2 in pages:
		pages.add(pagec-1)

	pages = list(sorted(pages))
	tmp = []
	prev = 0
	for page in pages:
		if page - prev > 1:
			tmp.append('...')
		tmp.append(page)
		prev = page
	pages = tmp

	pages = [
		create_page_struct(limit, page, page == curpage, token)
		for page in pages
	]

	return pages





# END
