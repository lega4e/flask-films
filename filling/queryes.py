from bd.table  import *
from functools import reduce
from nvxlira   import Lira
from nvxstruct import struct
from random    import choice

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text as sqltext
from prettytable import PrettyTable as PT

Session = sessionmaker(bind=engine)





############################################################
# functions
def print_pretty(heads=None, fields=None):
	table = PT(heads if heads else [i for i in range(len(fields[0]))] )
	for f in fields:
		table.add_row(f)
	for name in table.field_names:
		table.align[name] = 'l'
	print(table)





############################################################
# prepare
session = Session()





############################################################
# main
top = session.query(Work).filter_by(atype='полнометражный фильм').order_by(Work.rt)[:20]
print_pretty(fields=[ (w.rt, w.name, w.year, w.atype) for w in top])

stmt = sqltext('select * from work join country on work = rt where country="Китай" order by rt limit 30')
q = session.query(Work).from_statement(stmt)
print_pretty(fields=[ (w.rt, w.name, w.year, w.base) for w in q ])

q = session.query(Work).join(Tag).filter(Tag.tag == 'спасение близких')[:20]
print_pretty(fields=[
	(w.rt, w.name[:20], w.year, w.base,
		', '.join(sorted(list(map(lambda g: g.genre, w.genre)))))
	for w in q
])
