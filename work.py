#-*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from setting import DB_URL
from datetime import datetime, timedelta
import re


Week = {u'월' : 0, u'화' : 1, u'수' : 2, u'목' : 3, u'금' : 4, u'토' : 5, u'일' : 6}

Base = declarative_base()

class Work(Base):
    __tablename__ = 'work'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    due = Column(DateTime, nullable=True)
    finished = Column(DateTime, nullable=True)
    done = Column(Boolean)

    def __init__(self, name, due=None):
        self.name = name
        # Due 형식
        # ~주 ~요일 ()
        # 날짜 : (~월) ~일 ~시 ~분(반), (~월) ~일 ~시, (~월) ~일
        # 월일시분, 월일시, 월일
        parse = re.search(ur'(다+음|이번)주\s+([월화수목금토일])요일\s*(.*)', due.decode('utf-8'))
        if parse:
            week_origin = None
            if parse.group(1) == u'이번':
                week_origin = datetime.today() - timedelta(days=datetime.today().weekday())
            else:
                week_origin = datetime.today() + timedelta(weeks=len(parse.group(1))-1) - timedelta(days=datetime.today().weekday())
            self.due = (week_origin + timedelta(days=Week[parse.group(2)])).replace(hour=0, minute=0, second=0, microsecond=0)

        self.finished = None
        self.done = False

    def __repr__(self):
        return (self.name + (' - %s까지' % (self.due) if self.due != None else ''))

engine = create_engine(DB_URL)
dbSession = sessionmaker()
dbSession.configure(bind=engine)
dao = None


def init_db():
    Base.metadata.create_all(engine)
    global dao
    dao = dbSession()


def reset_db():
    for table in reversed(Base.metadata.sorted_tables):
        engine.execute(table.delete())
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
