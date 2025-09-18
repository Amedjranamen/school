from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal
from datetime import datetime
import uuid

# User Models
class UserRole(str):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    TEACHER = "teacher"
    STUDENT = "student"

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    role: Literal["admin", "librarian", "teacher", "student"]
    class_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    class_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    active: Optional[bool] = None

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Book Models
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    authors: List[str] = Field(..., min_items=1)
    isbn: Optional[str] = Field(None, max_length=20)
    publisher: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1000, le=2030)
    description: Optional[str] = Field(None, max_length=2000)
    categories: List[str] = Field(default_factory=list)
    cover_url: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)

class BookCreate(BookBase):
    total_copies: int = Field(1, ge=1)

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    authors: Optional[List[str]] = Field(None, min_items=1)
    isbn: Optional[str] = Field(None, max_length=20)
    publisher: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1000, le=2030)
    description: Optional[str] = Field(None, max_length=2000)
    categories: Optional[List[str]] = None
    cover_url: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    total_copies: Optional[int] = Field(None, ge=1)

class Book(BookBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    total_copies: int = Field(1, ge=1)
    available_copies: int = Field(1, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Loan Models
class LoanStatus(str):
    BORROWED = "borrowed"
    RETURNED = "returned"
    OVERDUE = "overdue"

class LoanBase(BaseModel):
    user_id: str
    book_id: str

class LoanCreate(LoanBase):
    due_days: Optional[int] = Field(14, ge=1, le=90)  # Default 14 days

class Loan(LoanBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    borrowed_at: datetime = Field(default_factory=datetime.utcnow)
    due_at: datetime
    returned_at: Optional[datetime] = None
    status: Literal["borrowed", "returned", "overdue"] = "borrowed"
    fine: float = Field(0.0, ge=0)

# Reservation Models
class ReservationStatus(str):
    WAITING = "waiting"
    AVAILABLE = "available"
    CANCELLED = "cancelled"
    FULFILLED = "fulfilled"

class ReservationBase(BaseModel):
    user_id: str
    book_id: str

class ReservationCreate(ReservationBase):
    pass

class Reservation(ReservationBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reserved_at: datetime = Field(default_factory=datetime.utcnow)
    status: Literal["waiting", "available", "cancelled", "fulfilled"] = "waiting"
    notified_at: Optional[datetime] = None

# Auth Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Response Models
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    class_name: Optional[str]
    phone: Optional[str]
    active: bool
    created_at: datetime

class BookResponse(BaseModel):
    id: str
    title: str
    authors: List[str]
    isbn: Optional[str]
    publisher: Optional[str]
    year: Optional[int]
    description: Optional[str]
    categories: List[str]
    cover_url: Optional[str]
    location: Optional[str]
    tags: List[str]
    total_copies: int
    available_copies: int
    created_at: datetime
    updated_at: datetime

class LoanResponse(BaseModel):
    id: str
    user_id: str
    book_id: str
    borrowed_at: datetime
    due_at: datetime
    returned_at: Optional[datetime]
    status: str
    fine: float
    user: Optional[UserResponse] = None
    book: Optional[BookResponse] = None