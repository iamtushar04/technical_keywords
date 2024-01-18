from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, UniqueConstraint, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Keywords(Base):
    __tablename__ = "keywords"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    keyword = Column("keyword", Text)
    tech_words = Column("tech_words", Text)
    inserted_at = Column("inserted_at", DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow())
    updated_at = Column("updated_at", DateTime(timezone=True), onupdate=func.now(), default=datetime.utcnow())
    __table_args__ = (
        UniqueConstraint('keyword'),
    )

    def __init__(self, keyword, tech_words, inserted_at, updated_at):
        self.keyword = keyword
        self.tech_words = tech_words
        self.inserted_at = inserted_at
        self.updated_at = updated_at

    def __repr__(self):
        return f"({self.keyword} {self.tech_words})"

