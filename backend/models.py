from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    entries = relationship('Entry', back_populates='user')

class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    mood_score = Column(Integer)
    user = relationship('User', back_populates='entries')
    analysis = relationship('Analysis', back_populates='entry', uselist=False)

class Analysis(Base):
    __tablename__ = 'analyses'
    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey('entries.id'), nullable=False, unique=True)
    result = Column(JSON, nullable=False)  # GPT çıktısı JSONB olarak saklanacak
    entry = relationship('Entry', back_populates='analysis') 