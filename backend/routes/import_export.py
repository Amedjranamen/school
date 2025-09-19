from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
import csv
import io
import json
import uuid
from auth import get_current_user, require_role
from models import User, BookCreate, UserCreate
from database import books_collection, users_collection, loans_collection
from passlib.context import CryptContext

router = APIRouter(prefix="/api/import-export", tags=["import-export"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/books/import")
async def import_books_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(["admin", "librarian"]))
):
    """Import books from CSV file"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Read and parse CSV
    contents = await file.read()
    csv_data = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    
    results = {
        "created": 0,
        "updated": 0,
        "errors": [],
        "duplicates": 0
    }
    
    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
        try:
            # Validate required fields
            required_fields = ['title', 'authors', 'total_copies']
            missing_fields = [field for field in required_fields if not row.get(field)]
            
            if missing_fields:
                results["errors"].append({
                    "row": row_num,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                })
                continue
            
            # Parse authors (assuming comma-separated)
            authors = [author.strip() for author in row['authors'].split(',')]
            
            # Parse categories (assuming comma-separated)
            categories = []
            if row.get('categories'):
                categories = [cat.strip() for cat in row['categories'].split(',')]
            
            # Check if book exists by ISBN or title+authors
            isbn = row.get('isbn', '').strip()
            existing_book = None
            
            if isbn:
                existing_book = await books_collection.find_one({"isbn": isbn})
            else:
                # Check by title and first author
                existing_book = await books_collection.find_one({
                    "title": row['title'].strip(),
                    "authors": {"$in": [authors[0]]}
                })
            
            total_copies = int(row['total_copies'])
            
            if existing_book:
                # Update existing book (add copies)
                new_total = existing_book.get('total_copies', 0) + total_copies
                new_available = existing_book.get('available_copies', 0) + total_copies
                
                await books_collection.update_one(
                    {"id": existing_book["id"]},
                    {
                        "$set": {
                            "total_copies": new_total,
                            "available_copies": new_available,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                results["updated"] += 1
            else:
                # Create new book
                book_doc = {
                    "id": str(uuid.uuid4()),
                    "title": row['title'].strip(),
                    "authors": authors,
                    "isbn": isbn if isbn else None,
                    "publisher": row.get('publisher', '').strip() or None,
                    "year": int(row['year']) if row.get('year', '').strip().isdigit() else None,
                    "description": row.get('description', '').strip() or None,
                    "categories": categories,
                    "cover_url": row.get('cover_url', '').strip() or None,
                    "total_copies": total_copies,
                    "available_copies": total_copies,
                    "location": row.get('location', '').strip() or None,
                    "tags": [],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await books_collection.insert_one(book_doc)
                results["created"] += 1
                
        except ValueError as e:
            results["errors"].append({
                "row": row_num,
                "error": f"Invalid data format: {str(e)}"
            })
        except Exception as e:
            results["errors"].append({
                "row": row_num,
                "error": f"Unexpected error: {str(e)}"
            })
    
    return results

@router.post("/users/import")
async def import_users_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(["admin"]))
):
    """Import users from CSV file (Admin only)"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Read and parse CSV
    contents = await file.read()
    csv_data = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    
    results = {
        "created": 0,
        "errors": [],
        "duplicates": 0
    }
    
    for row_num, row in enumerate(csv_reader, start=2):
        try:
            # Validate required fields
            required_fields = ['username', 'email', 'full_name', 'role']
            missing_fields = [field for field in required_fields if not row.get(field)]
            
            if missing_fields:
                results["errors"].append({
                    "row": row_num,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                })
                continue
            
            # Check if user already exists
            existing_user = await users_collection.find_one({
                "$or": [
                    {"email": row['email'].strip()},
                    {"username": row['username'].strip()}
                ]
            })
            
            if existing_user:
                results["duplicates"] += 1
                results["errors"].append({
                    "row": row_num,
                    "error": f"User {row['username']} already exists"
                })
                continue
            
            # Generate default password if not provided
            password = row.get('password', '').strip()
            if not password:
                password = f"{row['username'].strip()}123"  # Default pattern
            
            # Hash password
            hashed_password = pwd_context.hash(password)
            
            # Create user document
            user_doc = {
                "id": str(uuid.uuid4()),
                "username": row['username'].strip(),
                "email": row['email'].strip(),
                "password_hash": hashed_password,
                "role": row['role'].strip(),
                "full_name": row['full_name'].strip(),
                "class": row.get('class', '').strip() or None,
                "phone": row.get('phone', '').strip() or None,
                "active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert user
            await users_collection.insert_one(user_doc)
            results["created"] += 1
            
        except Exception as e:
            results["errors"].append({
                "row": row_num,
                "error": str(e)
            })
    
    return results

@router.get("/books/export")
async def export_books_csv(
    category: Optional[str] = Query(None),
    current_user: User = Depends(require_role(["admin", "librarian"]))
):
    """Export books to CSV file"""
    
    # Build filter query
    filter_query = {}
    if category:
        filter_query["categories"] = {"$in": [category]}
    
    # Get books
    books = await books_collection.find(filter_query).to_list(None)
    
    # Create CSV content
    output = io.StringIO()
    fieldnames = [
        'id', 'title', 'authors', 'isbn', 'publisher', 'year', 
        'description', 'categories', 'total_copies', 'available_copies',
        'location', 'cover_url', 'created_at'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for book in books:
        # Convert arrays to comma-separated strings
        book_row = {
            'id': book.get('id'),
            'title': book.get('title'),
            'authors': ', '.join(book.get('authors', [])),
            'isbn': book.get('isbn'),
            'publisher': book.get('publisher'),
            'year': book.get('year'),
            'description': book.get('description'),
            'categories': ', '.join(book.get('categories', [])),
            'total_copies': book.get('total_copies'),
            'available_copies': book.get('available_copies'),
            'location': book.get('location'),
            'cover_url': book.get('cover_url'),
            'created_at': book.get('created_at')
        }
        writer.writerow(book_row)
    
    # Create response
    output.seek(0)
    response = StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=books_export.csv"}
    )
    
    return response

@router.get("/users/export")
async def export_users_csv(
    role: Optional[str] = Query(None),
    current_user: User = Depends(require_role(["admin"]))
):
    """Export users to CSV file (Admin only)"""
    
    # Build filter query
    filter_query = {}
    if role:
        filter_query["role"] = role
    
    # Get users (exclude password_hash)
    projection = {
        "password_hash": 0,
        "_id": 0
    }
    users = await users_collection.find(filter_query, projection).to_list(None)
    
    # Create CSV content
    output = io.StringIO()
    fieldnames = [
        'id', 'username', 'email', 'full_name', 'role', 
        'class', 'phone', 'active', 'created_at'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for user in users:
        writer.writerow(user)
    
    # Create response
    output.seek(0)
    response = StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )
    
    return response

@router.get("/loans/export")
async def export_loans_csv(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_role(["admin", "librarian"]))
):
    """Export loans to CSV file"""
    
    # Build filter query
    filter_query = {}
    
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        filter_query["borrowed_at"] = date_filter
    
    if status:
        filter_query["status"] = status
    
    # Aggregation pipeline to get detailed loan data
    pipeline = [
        {"$match": filter_query},
        {"$lookup": {
            "from": "books",
            "localField": "book_id",
            "foreignField": "id",
            "as": "book_info"
        }},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user_info"
        }},
        {"$unwind": "$book_info"},
        {"$unwind": "$user_info"},
        {"$project": {
            "loan_id": "$id",
            "book_title": "$book_info.title",
            "book_authors": {"$reduce": {
                "input": "$book_info.authors",
                "initialValue": "",
                "in": {"$concat": ["$$value", {"$cond": [{"$eq": ["$$value", ""]}, "", ", "]}, "$$this"]}
            }},
            "book_isbn": "$book_info.isbn",
            "user_name": "$user_info.full_name",
            "user_email": "$user_info.email",
            "user_role": "$user_info.role",
            "user_class": "$user_info.class",
            "borrowed_at": 1,
            "due_at": 1,
            "returned_at": 1,
            "status": 1,
            "fine": 1
        }},
        {"$sort": {"borrowed_at": -1}}
    ]
    
    loans = await loans_collection.aggregate(pipeline).to_list(None)
    
    # Create CSV content
    output = io.StringIO()
    fieldnames = [
        'loan_id', 'book_title', 'book_authors', 'book_isbn',
        'user_name', 'user_email', 'user_role', 'user_class',
        'borrowed_at', 'due_at', 'returned_at', 'status', 'fine'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for loan in loans:
        writer.writerow(loan)
    
    # Create response
    output.seek(0)
    response = StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=loans_export.csv"}
    )
    
    return response

@router.get("/template/books")
async def get_books_import_template():
    """Get CSV template for books import"""
    
    template_data = [
        {
            'title': 'Exemple Livre',
            'authors': 'Auteur Un, Auteur Deux',
            'isbn': '978-2-1234-5678-9',
            'publisher': 'Éditions Exemple',
            'year': '2023',
            'description': 'Description du livre...',
            'categories': 'Fiction, Jeunesse',
            'total_copies': '3',
            'location': 'Rayon A - Étagère 1',
            'cover_url': 'https://example.com/cover.jpg'
        }
    ]
    
    output = io.StringIO()
    fieldnames = [
        'title', 'authors', 'isbn', 'publisher', 'year', 
        'description', 'categories', 'total_copies', 'location', 'cover_url'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in template_data:
        writer.writerow(row)
    
    output.seek(0)
    response = StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=books_import_template.csv"}
    )
    
    return response

@router.get("/template/users")
async def get_users_import_template():
    """Get CSV template for users import"""
    
    template_data = [
        {
            'username': 'jean.martin',
            'email': 'jean.martin@ecole.fr',
            'full_name': 'Jean Martin',
            'role': 'student',
            'class': '6ème A',
            'phone': '0123456789',
            'password': 'jean123'
        }
    ]
    
    output = io.StringIO()
    fieldnames = ['username', 'email', 'full_name', 'role', 'class', 'phone', 'password']
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in template_data:
        writer.writerow(row)
    
    output.seek(0)
    response = StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_import_template.csv"}
    )
    
    return response