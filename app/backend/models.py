from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, text
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), 
                        nullable=False, server_default=text('NOW()'))
    
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    file_path = Column(Text, nullable=False, unique=True)
    persist_path = Column(Text, nullable=False)
    uploaded_at = Column(TIMESTAMP(timezone=True), 
                        nullable=False, server_default=text('NOW()'))
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at =  Column(TIMESTAMP(timezone=True), 
                        nullable=False, server_default=text('NOW()'))
    
    document_id = Column(Integer, ForeignKey("documents.id", ondelete='CASCADE'), nullable=False)
