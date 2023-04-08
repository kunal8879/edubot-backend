from sqlalchemy import String, Integer, Column
from py.db_config import Base


class Question(Base):
    __tablename__ = 'unanswered_questions'
    id = Column(Integer, primary_key=True, index=True)
    chat = Column(String)
    time = Column(String)


class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)


