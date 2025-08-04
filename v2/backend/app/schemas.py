from pydantic import BaseModel
from typing import List, Optional
import datetime

class TaskBase(BaseModel):
    ticker: str
    date: str

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: str
    status: str
    result: Optional[str] = None
    created_at: datetime.datetime
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    tasks: List[Task] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
