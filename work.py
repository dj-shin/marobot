#-*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from setting import DB_URL
from datetime import datetime


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
        if due != None:
            if len(due) == 4:
                self.due = datetime(datetime.today().year, int(due[:2]), int(due[2:4]))
            elif len(due) == 6:
                self.due = datetime(datetime.today().year, int(due[:2]), int(due[2:4]), hour=int(due[4:6]))
            elif len(due) == 8:
                self.due = datetime(datetime.today().year, int(due[:2]), int(due[2:4]), hour=int(due[4:6]), minute=int(due[6:8]))
            else:
                self.due = None
        else:
            self.due = None
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
