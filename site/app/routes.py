# app/routes.py
from app    import flask, bd
from flask  import render_template, request
from nvxsct import sct

from app.mescaline import generate_page_list, generate_search_hint
from app.bd        import create_sets_struct





@flask.route('/')
@flask.route('/index')
def index_url():
	return render_template('index.html')



@flask.route('/common', methods=['get', 'post'])
def common_url():
	token = None
	sets  = create_sets_struct()

	# Если выставлены параметры поиска
	if request.method.lower() == 'post':
		sets.offset = 0

		sets.atype   = request.form.get('type')
		sets.genre   = request.form.get('genre')
		sets.country = request.form.get('country')
		sets.tag     = request.form.get('tag')
		sets.sorting = request.form.get('sorting')
		sets.limit   = int(request.form.get('limit'))

		try:
			sets.minyear = int(request.form.get('min-year', bd.minyear))
			sets.maxyear = int(request.form.get('max-year', bd.maxyear))
		except:
			pass
		print(sets.minyear, sets.maxyear, flush=True)
	else:
		token = request.args.get('token')
		try:
			sets.offset = int(request.args.get('offset', 0))
			sets.limit  = int(request.args.get('limit',  50))
		except:
			pass

	return render_rating_template(sets, token)



@flask.route('/search', methods=['get', 'post'])
def search_url():
	if request.method.lower() == 'post':
		return common_url()

	sets = create_sets_struct()
	sets.country  = request.args.get('country',  'Не выбрано')
	sets.atype    = request.args.get('atype',    'Не выбрано')
	sets.genre    = request.args.get('genre',    'Не выбрано')
	sets.base     = request.args.get('base',     'Не выбрано')
	sets.director = request.args.get('director', 'Не выбрано')
	sets.idea     = request.args.get('idea',     'Не выбрано')
	sets.actor    = request.args.get('actor',    'Не выбрано')
	sets.tag      = request.args.get('tag',      'Не выбрано')

	return render_rating_template(sets, None)



@flask.route('/search_text', methods=['get', 'post'])
def search_text_url():
	if request.method.lower() == 'post':
		return common_url()

	sets = create_sets_struct()
	sets.like = request.args.get('text', None)

	return render_rating_template(sets, None)



@flask.route('/work')
def work_url():
	try:    work = bd.get_work(int(request.args.get('id')))
	except: return 'Unknown work Id'

	work.cntry  = [ str(c.country.country)           for c in work.country ]
	work.gnrs   = [ str(c.genre.genre)               for c in work.genre   ]
	work.actrs  = [ str(c.actor.actor)               for c in work.actor   ]
	work.tags   = [ (c.tag.tag, c.score, c.tag.desc) for c in work.tag     ]
	work.drctr  = work.director.director if work.director else None
	work.anidea = work.idea.idea         if work.idea     else None

	return render_template('work.html', work=work, title=work.name)





def render_rating_template(sets, token):
	'''
	Вспомогательная функция, которая возращает
	отрендеренную html-страницу, заполненную
	полученными на основе настроек или токена
	работами
	'''
	offset       = sets.offset
	limit        = sets.limit
	works, extra = bd.get_rating(sets, token)
	sets         = extra.sets

	# set count of all works
	for w in works:
		w.cntry = ', '.join([ c.country.country for c in w.country ])

	return render_template(
		'rating.html',
		title       = 'Рейтинг',
		header      = (
			'Рейтинг с %i по %i' % (offset+1, offset + len(works))
			if len(works) != 0 else 'Ничего не найдено'
		),
		works       = works,
		prev_offset = sct(v=max(offset-limit, 0)) if offset != 0                       else None,
		next_offset = sct(v=offset + limit)       if offset + limit < extra.count else None,
		next_limit  = sct(v=min(limit, extra.count-offset-limit)),
		genres      = [ 'Не выбрано' ] + bd.genres,
		types       = [ 'Не выбрано' ] + bd.types,
		tags        = [ 'Не выбрано' ] + bd.tags,
		countries   = [ 'Не выбрано' ] + bd.countries,
		sorting     = [
			'По расчётному баллу (возр.)',
			'По расчётному баллу (убыв.)',
			'По среднему баллу (возр.)',
			'По среднему баллу (убыв.)',
			'По году (возр.)',
			'По году (убыв.)',
			'По названию (возр.)',
			'По названию (убыв.)',
			'По количеству голосов (возр.)',
			'По количеству голосов (убыв.)',
		],
		token       = sct(v=extra.token) if extra.token is not None else None,
		sets        = sets,
		search_hint = generate_search_hint(sets),
		pagelist    = generate_page_list(extra.count, offset, limit, extra.token),
		work_count  = extra.count
	)






# END
