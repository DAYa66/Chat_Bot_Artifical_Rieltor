from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String,ForeignKey, DATETIME

Base = declarative_base()

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    descript = Column(String)
