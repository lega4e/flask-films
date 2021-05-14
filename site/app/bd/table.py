#
# Файл содержит определение таблиц базы данных
#
############################################################
# import
import sqlalchemy as sql

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Column, ForeignKey
from sqlalchemy.types           import *
from sqlalchemy.orm             import relationship





############################################################
# Create main objects
engine = sql.create_engine(
	"mysql+pymysql://debian-sys-maint:q1U7whK9tj9W8xwK@localhost/film",
	#  echo=True
)

Base = declarative_base(engine)





############################################################
# Create work table
class Work(Base):
	__tablename__ = 'work'
	work_id     = Column(Integer, nullable=False, primary_key=True)
	name        = Column(String(120))
	year        = Column(Integer)
	atype       = Column(String(120))
	dur         = Column(Integer)
	epsc        = Column(Integer)
	base        = Column(String(60))
	director_id = Column(Integer, ForeignKey('director.director_id'))
	idea_id     = Column(Integer, ForeignKey('idea.idea_id'))
	score       = Column(Float)       # hidden
	bscore      = Column(Float)       # hidden
	voted       = Column(Integer)     # hidden
	imgref      = Column(String(120)) # hidden
	ann         = Column(String(8000))

	'''
	relations:
	Work.country  = relationship('Country',   back_populates='work')
	Work.genre    = relationship('WorkGenre', back_populates='work')
	Work.director = relationship('Director',  back_populates='work')
	Work.idea     = relationship('Idea',      back_populates='work')
	Work.actor    = relationship('WorkActor', back_populates='work')
	Work.tag      = relationship('WorkTag',   back_populates='work')
	'''





############################################################
# Create country table
class Country(Base):
	__tablename__ = 'country'
	country_id = Column(Integer,    primary_key=True)
	country    = Column(String(60), nullable=False)



class WorkCountry(Base):
	__tablename__ = 'work_country'
	id         = Column(Integer, primary_key=True)
	work_id    = Column(Integer, ForeignKey('work.work_id'),       nullable=False)
	country_id = Column(Integer, ForeignKey('country.country_id'), nullable=False)
	order      = Column(Integer)

	work    = relationship('Work',    back_populates='country')
	country = relationship('Country', back_populates='work')

Work.country = relationship('WorkCountry', back_populates='work')
Country.work = relationship('WorkCountry', back_populates='country')





############################################################
# Create genre table
class Genre(Base):
	__tablename__ = 'genre'
	genre_id = Column(Integer,     primary_key=True)
	genre    = Column(String(120), nullable=False)



class WorkGenre(Base):
	__tablename__ = 'work_genre'
	id       = Column(Integer, primary_key=True)
	work_id  = Column(Integer, ForeignKey('work.work_id'),   nullable=False)
	genre_id = Column(Integer, ForeignKey('genre.genre_id'), nullable=False)

	work  = relationship('Work',  back_populates='genre')
	genre = relationship('Genre', back_populates='work')

Work.genre = relationship('WorkGenre', back_populates='work')
Genre.work = relationship('WorkGenre', back_populates='genre')





############################################################
# Create director table
class Director(Base):
	__tablename__ = 'director'
	director_id = Column(Integer,     primary_key=True)
	director    = Column(String(120), nullable=False)

	work = relationship('Work', back_populates='director')

Work.director = relationship('Director', back_populates='work')





############################################################
# Create idea table
class Idea(Base):
	__tablename__ = 'idea'
	idea_id = Column(Integer,     primary_key=True)
	idea    = Column(String(120), nullable=False)

	work = relationship('Work', back_populates='idea')

Work.idea = relationship('Idea', back_populates='work')





############################################################
# Create actor table
class Actor(Base):
	__tablename__ = 'actor'
	actor_id = Column(Integer,     primary_key=True)
	actor    = Column(String(120), nullable=False)



class WorkActor(Base):
	__tablename__ = 'work_actor'
	id       = Column(Integer, primary_key=True)
	work_id  = Column(Integer, ForeignKey('work.work_id'),   nullable=False)
	actor_id = Column(Integer, ForeignKey('actor.actor_id'), nullable=False)
	order    = Column(Integer)

	work  = relationship('Work',  back_populates='actor')
	actor = relationship('Actor', back_populates='work')

Work.actor = relationship('WorkActor', back_populates='work')
Actor.work = relationship('WorkActor', back_populates='actor')





############################################################
# Create tag table
class Tag(Base):
	__tablename__ = 'tag'
	tag_id = Column(Integer,     primary_key=True)
	tag    = Column(String(120), nullable=False)
	desc   = Column(String(3000))



class WorkTag(Base):
	__tablename__ = 'work_tag'
	id      = Column(Integer, primary_key=True)
	work_id = Column(Integer, ForeignKey('work.work_id'), nullable=False)
	tag_id  = Column(Integer, ForeignKey('tag.tag_id'),   nullable=False)
	score   = Column(Float)

	work = relationship('Work', back_populates='tag')
	tag  = relationship('Tag', back_populates='work')

Work.tag = relationship('WorkTag', back_populates='work')
Tag.work = relationship('WorkTag', back_populates='tag')





############################################################
# END
