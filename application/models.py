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
    date = Column(String, nullable=False)
    area = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    author = Column(String, default='anonymous')
    created_at = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    status = Column(String, default='active')


# Set database path to project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_URI = f'sqlite:///{PROJECT_ROOT / "annotations.db"}'

engine = create_engine(DATABASE_URI, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
