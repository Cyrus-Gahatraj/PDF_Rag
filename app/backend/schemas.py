from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: int
    email: EmailStr
    username: str

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None


class Document(BaseModel):
    id: int
    name: str
    file_path: str
    persist_path: str
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)

class QueryRequest(BaseModel):
    document_id: int
    question: str

class Query(QueryRequest):
    id: int
    answer: str
