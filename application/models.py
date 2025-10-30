from datetime import datetime
from pathlib import Path
from sqlalchemy import (Column, Integer, String, DateTime, Text)
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / 'annotations.db'
DATABASE_URL = f'sqlite:///{DB_PATH.as_posix()}'

Base = declarative_base()


class Annotation(Base):
    __tablename__ = 'annotations'
    id = Column(String(36), primary_key=True)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    area = Column(String(10), nullable=False)
    text = Column(Text, nullable=False)
    author = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    status = Column(String(20), default='active')


def get_engine():
    # ensure parent exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db(engine=None):
    eng = engine or get_engine()
    Base.metadata.create_all(eng)


def get_session(engine=None):
    eng = engine or get_engine()
    Session = sessionmaker(bind=eng)
    return Session()
