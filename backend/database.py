from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List
from models import User, Book, Loan, Reservation, UserCreate, BookCreate, LoanCreate, ReservationCreate
from auth import get_password_hash
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Collections
users_collection = db.users
books_collection = db.books
loans_collection = db.loans
reservations_collection = db.reservations

# User operations
async def create_user(user_data: UserCreate) -> User:
    """Create a new user."""
    # Check if user already exists
    existing_user = await users_collection.find_one({"$or": [{"username": user_data.username}, {"email": user_data.email}]})
    if existing_user:
        raise ValueError("User with this username or email already exists")
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user object
    user = User(
        **user_data.dict(exclude={"password"}),
        password_hash=hashed_password
    )
    
    # Insert into database
    await users_collection.insert_one(user.dict())
    return user

async def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username."""
    user_doc = await users_collection.find_one({"username": username})
    if user_doc:
        return User(**user_doc)
    return None

async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID."""
    user_doc = await users_collection.find_one({"id": user_id})
    if user_doc:
        return User(**user_doc)
    return None

async def get_users(skip: int = 0, limit: int = 50, role: Optional[str] = None) -> List[User]:
    """Get users with pagination and filtering."""
    query = {}
    if role:
        query["role"] = role
    
    cursor = users_collection.find(query).skip(skip).limit(limit)
    users = []
    async for user_doc in cursor:
        users.append(User(**user_doc))
    return users

# Book operations
async def create_book(book_data: BookCreate) -> Book:
    """Create a new book."""
    book = Book(
        **book_data.dict(),
        available_copies=book_data.total_copies
    )
    
    await books_collection.insert_one(book.dict())
    return book

async def get_book_by_id(book_id: str) -> Optional[Book]:
    """Get book by ID."""
    book_doc = await books_collection.find_one({"id": book_id})
    if book_doc:
        return Book(**book_doc)
    return None

async def get_books(skip: int = 0, limit: int = 50, search: Optional[str] = None, category: Optional[str] = None, available: Optional[bool] = None) -> List[Book]:
    """Get books with pagination, search and filtering."""
    query = {}
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"authors": {"$regex": search, "$options": "i"}},
            {"isbn": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    if category:
        query["categories"] = category
    
    if available is True:
        query["available_copies"] = {"$gt": 0}
    elif available is False:
        query["available_copies"] = 0
    
    cursor = books_collection.find(query).skip(skip).limit(limit)
    books = []
    async for book_doc in cursor:
        books.append(Book(**book_doc))
    return books

async def update_book(book_id: str, book_data: dict) -> Optional[Book]:
    """Update a book."""
    book_data["updated_at"] = datetime.utcnow()
    result = await books_collection.update_one(
        {"id": book_id},
        {"$set": book_data}
    )
    
    if result.modified_count:
        return await get_book_by_id(book_id)
    return None

async def delete_book(book_id: str) -> bool:
    """Delete a book."""
    result = await books_collection.delete_one({"id": book_id})
    return result.deleted_count > 0

# Loan operations
async def create_loan(loan_data: LoanCreate) -> Optional[Loan]:
    """Create a new loan."""
    # Check if book is available
    book = await get_book_by_id(loan_data.book_id)
    if not book or book.available_copies <= 0:
        return None
    
    # Check if user already has this book
    existing_loan = await loans_collection.find_one({
        "user_id": loan_data.user_id,
        "book_id": loan_data.book_id,
        "status": "borrowed"
    })
    if existing_loan:
        return None
    
    # Create loan
    due_date = datetime.utcnow() + timedelta(days=loan_data.due_days)
    loan = Loan(
        user_id=loan_data.user_id,
        book_id=loan_data.book_id,
        due_at=due_date
    )
    
    # Update book availability
    await books_collection.update_one(
        {"id": loan_data.book_id},
        {"$inc": {"available_copies": -1}}
    )
    
    # Insert loan
    await loans_collection.insert_one(loan.dict())
    return loan

async def return_book(loan_id: str) -> Optional[Loan]:
    """Return a book."""
    loan_doc = await loans_collection.find_one({"id": loan_id, "status": "borrowed"})
    if not loan_doc:
        return None
    
    loan = Loan(**loan_doc)
    
    # Calculate fine if overdue
    now = datetime.utcnow()
    fine = 0.0
    if now > loan.due_at:
        overdue_days = (now - loan.due_at).days
        fine = overdue_days * 0.5  # 50 cents per day
    
    # Update loan
    await loans_collection.update_one(
        {"id": loan_id},
        {
            "$set": {
                "returned_at": now,
                "status": "returned",
                "fine": fine
            }
        }
    )
    
    # Update book availability
    await books_collection.update_one(
        {"id": loan.book_id},
        {"$inc": {"available_copies": 1}}
    )
    
    return await get_loan_by_id(loan_id)

async def get_loan_by_id(loan_id: str) -> Optional[Loan]:
    """Get loan by ID."""
    loan_doc = await loans_collection.find_one({"id": loan_id})
    if loan_doc:
        return Loan(**loan_doc)
    return None

async def get_loans(skip: int = 0, limit: int = 50, user_id: Optional[str] = None, status: Optional[str] = None) -> List[Loan]:
    """Get loans with pagination and filtering."""
    query = {}
    if user_id:
        query["user_id"] = user_id
    if status:
        query["status"] = status
    
    cursor = loans_collection.find(query).skip(skip).limit(limit).sort("borrowed_at", -1)
    loans = []
    async for loan_doc in cursor:
        loans.append(Loan(**loan_doc))
    return loans

# Update overdue loans (should be run periodically)
async def update_overdue_loans():
    """Update overdue loans status."""
    now = datetime.utcnow()
    await loans_collection.update_many(
        {"due_at": {"$lt": now}, "status": "borrowed"},
        {"$set": {"status": "overdue"}}
    )

# Reservation operations
async def create_reservation(reservation_data: ReservationCreate) -> Reservation:
    """Create a new reservation."""
    reservation = Reservation(**reservation_data.dict())
    await reservations_collection.insert_one(reservation.dict())
    return reservation

async def get_reservations(skip: int = 0, limit: int = 50, user_id: Optional[str] = None, book_id: Optional[str] = None) -> List[Reservation]:
    """Get reservations with filtering."""
    query = {}
    if user_id:
        query["user_id"] = user_id
    if book_id:
        query["book_id"] = book_id
    
    cursor = reservations_collection.find(query).skip(skip).limit(limit).sort("reserved_at", 1)
    reservations = []
    async for reservation_doc in cursor:
        reservations.append(Reservation(**reservation_doc))
    return reservations