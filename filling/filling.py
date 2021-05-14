#!/usr/bin/python3
############################################################
# import
from bd.table  import *
from functools import reduce
from nvxlira   import Lira
from nvxsct    import sct
from random    import choice

from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)





############################################################
# main
lira = Lira('parse/works.bin', 'parse/hworks.bin')
print(len(lira['work']))
print(lira.get(choice(lira['work'])).pretty())

create_all()

session = Session()





############################################################
# Countryies
countries = set()
for work in [ lira(id) for id in lira['work'] ]:
	for c in work.country:
		countries.add(c.country)

countries = sorted(list(countries))
countries = { countries[i] : i+1 for i in range(len(countries)) }
print(*countries.items(), sep='\n')

for country, id in countries.items():
	session.add(Country(country_id=id, country=country))

session.commit()





############################################################
# Genres
genres = set()
for work in [ lira(id) for id in lira['work'] ]:
	for g in work.genre:
		genres.add(g)

genres = sorted(filter(lambda x: x != '', list(genres)))
genres = { genres[i] : i+1 for i in range(len(genres)) }
print(*genres, sep='\n')

for genre, id in genres.items():
	session.add(Genre(genre_id=id, genre=genre))

session.commit()





############################################################
# Directors
directors = set()
for work in [ lira(id) for id in lira['work'] ]:
	if work.director:
		directors.add(work.director)

directors = sorted(filter(lambda x: x != '', list(directors)))
directors = { directors[i] : i+1 for i in range(len(directors)) }
print(*directors, sep='\n')

for director, id in directors.items():
	session.add(Director(director_id=id, director=director))

session.commit()





############################################################
# Idea
ideas = set()
for work in [ lira(id) for id in lira['work'] ]:
	if work.idea:
		ideas.add(work.idea)

ideas = sorted(filter(lambda x: x != '', list(ideas)))
ideas = { ideas[i] : i+1 for i in range(len(ideas)) }
print(*ideas, sep='\n')

for idea, id in ideas.items():
	session.add(Idea(idea_id=id, idea=idea))

session.commit()





############################################################
# Actors
actors = set()
for work in [ lira(id) for id in lira['work'] ]:
	if work.actor:
		for actor in work.actor:
			actors.add(actor.actor)

actors = sorted(filter(lambda x: x != '', list(actors)))
actors = { actors[i] : i+1 for i in range(len(actors)) }
print(len(actors))
print(*actors.items(), sep='\n')

for actor, id in actors.items():
	session.add(Actor(actor_id=id, actor=actor))

session.commit()





############################################################
# Tag
tags = set()
tagdesc = {}
for work in [ lira(id) for id in lira['work'] ]:
	for tag in work.tag:
		tags.add(tag.tag)
		if tag.tag not in tagdesc:
			tagdesc[tag.tag] = tag.desc

tags = sorted(filter(lambda x: x != '', list(tags)))
tags = { tags[i] : i+1 for i in range(len(tags)) }
print(*tags.items(), sep='\n')

for tag, id in tags.items():
	session.add(Tag(tag_id=id, tag=tag, desc=tagdesc[tag]))

session.commit()





############################################################
# create works
work = lira(choice(lira['work']))
print(*work.work.__dict__.keys(), sep='\n')
print(work.director, directors[work.director])
print(work.idea, ideas[work.idea])

work_id = 1
for work in [ lira(id) for id in lira['work'] ]:
	session.add(Work(
		**work.work.__dict__,
		work_id     = work_id,
		director_id = directors[work.director] if work.director else None,
		idea_id     = ideas[work.idea]         if work.idea     else None
	))

	if work.country:
		for c in work.country:
			session.add(WorkCountry(
				work_id    = work_id,
				country_id = countries[c.country],
				order      = c.order
			))

	if work.genre:
		for g in work.genre:
			if not g:
				continue
			session.add(WorkGenre(
				work_id  = work_id,
				genre_id = genres[g]
			))

	if work.actor:
		for a in work.actor:
			if not a.actor:
				continue
			session.add(WorkActor(
				work_id  = work_id,
				actor_id = actors[a.actor],
				order    = a.order
			))

	if work.tag:
		for t in work.tag:
			session.add(WorkTag(
				work_id = work_id,
				tag_id  = tags[t.tag],
				score   = t.score
			))

	work_id += 1

#  session.rollback()

session.commit()





############################################################
# create tags desc
tags = {
	tag.tag : tag.desc
	for tag in reduce(lambda a, b: a + b, [
		lira.get(id).tag for id in lira['work']
	])
}

session.add_all([
	TagDesc(tag=tag, desc=desc) 
	for tag, desc in tags.items()
])
session.commit()
session.flush()





############################################################
# create works and other

works = [ lira.get(id) for id in lira['work'] ]
works.sort(key=lambda w: w.work.bscore, reverse=True)

for i in range(len(works)):
	works[i].work.rt = i+1

for w in works[:50]:
	print(w.work.rt, w.work.name)

for w in [ lira.get(id) for id in lira['work'] ]:
	session.add(Work(**w.work.__dict__))

	rt = w.work.rt
	for country in w.country:
		c = Country(work=rt, country=country)
		session.add(c)

	for genre in w.genre:
		g = Genre(work=rt, genre=genre)
		session.add(g)

	if w.director:
		session.add(Director(work=rt, director=w.director))

	if w.idea:
		session.add(Idea(work=rt, idea=w.idea))

	if w.actor:
		for i in range(len(w.actor)):
			session.add(Actor(work=rt, actor=w.actor[i], order=i+1))

	if w.ann:
		session.add(Ann(work=rt, ann=w.ann))

	for tag in w.tag:
		session.add(Tag(work=rt, tag=tag.tag, score=tag.score))

#  session.rollback()
session.flush()
session.commit()
session.dirty





############################################################
# other
for id in lira['work']:
	w = lira.get(id)
	if len(w.genre) != len(set(w.genre)):
		print(w.work.rt)
		w.genre = list(set(w.genre))
		lira.put(w, id=id, cat='work')

for id in lira['work']:
	w = lira.get(id)
	if w.actor is None:
		continue
	if len(w.actor) != len(set(w.actor)):
		print(w.work.rt)
		w.actor = list(set(w.actor))
		lira.put(w, id=id, cat='work')

for id in lira['work']:
	w = lira.get(id)
	if len(w.country) != len(set(w.country)):
		print(w.work.rt)
		w.country = list(set(w.country))
		lira.put(w, id=id, cat='work')

def has_duplicats(tags):
	for i in range(len(tags)):
		for j in range(i+1, len(tags)):
			if tags[i].tag == tags[j].tag:
				return (i, j)
	return None

for id in lira['work']:
	w = lira.get(id)
	was = False
	while True:
		dup = has_duplicats(w.tag)
		if dup is None:
			break
		was = True
		print(w.work.rt)
		del w.tag[dup[1]]
	lira.put(w, id=id, cat='work')

id = [ id for id in lira['work'] if lira.get(id).work.rt == 2654 ][0]
obj = lira.get(id)
print(obj.actor)
obj.actor.remove('Дэвид Келли')
lira.put(obj, id=id, cat='work')

id = [ id for id in lira['work'] if lira.get(id).work.rt == 7631 ][0]
obj = lira.get(id)
print(obj.genre)
obj.genre.remove('комедия')
lira.put(obj, id=id, cat='work')



session.flush()





############################################################
# END
