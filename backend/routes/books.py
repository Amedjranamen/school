from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from models import BookCreate, BookUpdate, BookResponse, User
from auth import get_current_active_user, require_librarian_or_admin
from database import (
    create_book, 
    get_books, 
    get_book_by_id, 
    update_book,
    delete_book
)

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/", response_model=List[BookResponse])
async def list_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search in title, authors, ISBN, description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of books with search and filtering."""
    books = await get_books(
        skip=skip, 
        limit=limit, 
        search=search, 
        category=category, 
        available=available
    )
    
    return [
        BookResponse(
            id=book.id,
            title=book.title,
            authors=book.authors,
            isbn=book.isbn,
            publisher=book.publisher,
            year=book.year,
            description=book.description,
            categories=book.categories,
            cover_url=book.cover_url,
            location=book.location,
            tags=book.tags,
            total_copies=book.total_copies,
            available_copies=book.available_copies,
            created_at=book.created_at,
            updated_at=book.updated_at
        )
        for book in books
    ]

@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific book by ID."""
    book = await get_book_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    return BookResponse(
        id=book.id,
        title=book.title,
        authors=book.authors,
        isbn=book.isbn,
        publisher=book.publisher,
        year=book.year,
        description=book.description,
        categories=book.categories,
        cover_url=book.cover_url,
        location=book.location,
        tags=book.tags,
        total_copies=book.total_copies,
        available_copies=book.available_copies,
        created_at=book.created_at,
        updated_at=book.updated_at
    )

@router.post("/", response_model=BookResponse)
async def create_new_book(
    book_data: BookCreate,
    current_user: User = Depends(require_librarian_or_admin)
):
    """Create a new book (librarian/admin only)."""
    book = await create_book(book_data)
    
    return BookResponse(
        id=book.id,
        title=book.title,
        authors=book.authors,
        isbn=book.isbn,
        publisher=book.publisher,
        year=book.year,
        description=book.description,
        categories=book.categories,
        cover_url=book.cover_url,
        location=book.location,
        tags=book.tags,
        total_copies=book.total_copies,
        available_copies=book.available_copies,
        created_at=book.created_at,
        updated_at=book.updated_at
    )

@router.put("/{book_id}", response_model=BookResponse)
async def update_book_info(
    book_id: str,
    book_data: BookUpdate,
    current_user: User = Depends(require_librarian_or_admin)
):
    """Update a book (librarian/admin only)."""
    # Check if book exists
    existing_book = await get_book_by_id(book_id)
    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Update book
    update_data = book_data.dict(exclude_unset=True)
    updated_book = await update_book(book_id, update_data)
    
    if not updated_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update book"
        )
    
    return BookResponse(
        id=updated_book.id,
        title=updated_book.title,
        authors=updated_book.authors,
        isbn=updated_book.isbn,
        publisher=updated_book.publisher,
        year=updated_book.year,
        description=updated_book.description,
        categories=updated_book.categories,
        cover_url=updated_book.cover_url,
        location=updated_book.location,
        tags=updated_book.tags,
        total_copies=updated_book.total_copies,
        available_copies=updated_book.available_copies,
        created_at=updated_book.created_at,
        updated_at=updated_book.updated_at
    )

@router.delete("/{book_id}")
async def delete_book_by_id(
    book_id: str,
    current_user: User = Depends(require_librarian_or_admin)
):
    """Delete a book (librarian/admin only)."""
    # Check if book exists
    existing_book = await get_book_by_id(book_id)
    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check if book has active loans
    from database import get_loans
    active_loans = await get_loans(limit=1, status="borrowed")
    for loan in active_loans:
        if loan.book_id == book_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete book with active loans"
            )
    
    success = await delete_book(book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete book"
        )
    
    return {"message": "Book deleted successfully"}