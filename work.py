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
    name = Column(String(128), unique=True, nullable=False)
    due = Column(DateTime, nullable=True)
    finished = Column(DateTime, nullable=True)
    done = Column(Boolean)

    def __init__(self, name, due_day, due_time):
        self.name = name
        # Due 형식
        # ~주 ~요일 ()
        # 날짜 : (~월) ~일 ~시 ~분(반), (~월) ~일 ~시, (~월) ~일
        # 월일시분, 월일시, 월일
        origin = datetime.today().replace(microsecond=0)
        
        if due_day is None:
            due_day = ''
        if due_time is None:
            due_time = ''

        parse = re.search(ur'(?P<week>다+음|이번)\s*주\s+(?P<weekday>[월화수목금토일])요일', due_day)
        if parse:
            origin -= timedelta(days=datetime.today().weekday())
            if parse.group('week') != u'이번':
                origin += timedelta(weeks=len(parse.group('week'))-1)
            origin += timedelta(days=Week[parse.group('weekday')])

        parse = re.search(ur'(?P<dayType>오늘|내일|모레|(?P<days>\d+)일\s*후)', due_day)
        if parse:
            if parse.group('dayType') == u'오늘':
                pass
            elif parse.group('dayType') == u'내일':
                origin += timedelta(days=1)
            elif parse.group('dayType') == u'모레':
                origin += timedelta(days=2)
            else:
                origin += timedelta(days=int(parse.group('days')))

        parse = re.search(ur'((?P<month>\d+)월)?\s*(?P<day>\d+)일', due_day)
        if parse:
            if parse.group('month'):
                origin = origin.replace(month=int(parse.group('month')))
            origin = origin.replace(day=int(parse.group('day')))

        parse = re.search(ur'(?P<hour>\d+)시\s*((?P<minute>\d+)분|반)?', due_time)
        if parse:
            origin = origin.replace(hour=int(parse.group('hour')), second=0)
            if parse.group('minute'):
                origin = origin.replace(minute=0)
            elif parse.group('minute') == u'반':
                origin = origin.replace(minute=30)
            else:
                origin = origin.replace(minute=int(parse.group('minute')))
        else:
            origin = origin.replace(hour=23, minute=59, second=59)

        self.due = origin

        self.finished = None
        self.done = False

    def __repr__(self):
        return (self.name + (' (%s)' % (self.due) if self.due != None else ''))

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
