from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserInDB(BaseModel):
    id: int
    username: str
    role: str
    ip: str
    timestamp: datetime
    password: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserAdminView(BaseModel):
    id: int
    username: str
    role: str
    ip: str
    timestamp: datetime