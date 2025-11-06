from datetime import datetime
from pathlib import Path
from sqlalchemy import (Column, Integer, String, DateTime, Text)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Annotation(Base):
    __tablename__ = 'annotations'
    
    id = Column(String, primary_key=True)
    # link anonymous annotations to cookie-based user id when present
    user_id = Column(String, nullable=True, index=True)
    date = Column(String, nullable=False)
    area = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    author = Column(String, default='anonymous')
    created_at = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    status = Column(String, default='active')


class CookieRecord(Base):
    __tablename__ = 'cookie_records'

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    accept_language = Column(String, nullable=True)
    fingerprint_hash = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # track how many page views (activities) this user has generated
    views = Column(Integer, default=0)
    # track how many annotations were created by this user
    annotations_count = Column(Integer, default=0)


# Set database path to project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_URI = f'sqlite:///{PROJECT_ROOT / "annotations.db"}'

engine = create_engine(DATABASE_URI, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
