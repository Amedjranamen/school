from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from models import LoanCreate, LoanResponse, User, UserResponse, BookResponse
from auth import get_current_active_user, require_librarian_or_admin, require_staff
from database import (
    create_loan, 
    get_loans, 
    get_loan_by_id, 
    return_book,
    get_user_by_id,
    get_book_by_id,
    update_overdue_loans
)

router = APIRouter(prefix="/loans", tags=["loans"])

@router.post("/", response_model=LoanResponse)
async def create_new_loan(
    loan_data: LoanCreate,
    current_user: User = Depends(require_staff)
):
    """Create a new loan (staff only)."""
    # Verify user and book exist
    user = await get_user_by_id(loan_data.user_id)
    book = await get_book_by_id(loan_data.book_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    loan = await create_loan(loan_data)
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create loan. Book may be unavailable or user already has this book."
        )
    
    return LoanResponse(
        id=loan.id,
        user_id=loan.user_id,
        book_id=loan.book_id,
        borrowed_at=loan.borrowed_at,
        due_at=loan.due_at,
        returned_at=loan.returned_at,
        status=loan.status,
        fine=loan.fine
    )

@router.get("/", response_model=List[LoanResponse])
async def list_loans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by status (borrowed, returned, overdue)"),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of loans with filtering."""
    # Students can only see their own loans
    if current_user.role == "student":
        user_id = current_user.id
    
    # Update overdue loans first
    await update_overdue_loans()
    
    loans = await get_loans(skip=skip, limit=limit, user_id=user_id, status=status)
    
    # Enrich with user and book information
    enriched_loans = []
    for loan in loans:
        loan_response = LoanResponse(
            id=loan.id,
            user_id=loan.user_id,
            book_id=loan.book_id,
            borrowed_at=loan.borrowed_at,
            due_at=loan.due_at,
            returned_at=loan.returned_at,
            status=loan.status,
            fine=loan.fine
        )
        
        # Add user info for staff
        if current_user.role in ["admin", "librarian", "teacher"]:
            user = await get_user_by_id(loan.user_id)
            if user:
                loan_response.user = UserResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    role=user.role,
                    class_name=user.class_name,
                    phone=user.phone,
                    active=user.active,
                    created_at=user.created_at
                )
        
        # Add book info
        book = await get_book_by_id(loan.book_id)
        if book:
            loan_response.book = BookResponse(
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
        
        enriched_loans.append(loan_response)
    
    return enriched_loans

@router.get("/my", response_model=List[LoanResponse])
async def get_my_loans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's loans."""
    await update_overdue_loans()
    
    loans = await get_loans(skip=skip, limit=limit, user_id=current_user.id, status=status)
    
    # Enrich with book information
    enriched_loans = []
    for loan in loans:
        loan_response = LoanResponse(
            id=loan.id,
            user_id=loan.user_id,
            book_id=loan.book_id,
            borrowed_at=loan.borrowed_at,
            due_at=loan.due_at,
            returned_at=loan.returned_at,
            status=loan.status,
            fine=loan.fine
        )
        
        # Add book info
        book = await get_book_by_id(loan.book_id)
        if book:
            loan_response.book = BookResponse(
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
        
        enriched_loans.append(loan_response)
    
    return enriched_loans

@router.put("/{loan_id}/return", response_model=LoanResponse)
async def return_loan(
    loan_id: str,
    current_user: User = Depends(require_staff)
):
    """Return a book (staff only)."""
    loan = await return_book(loan_id)
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found or already returned"
        )
    
    return LoanResponse(
        id=loan.id,
        user_id=loan.user_id,
        book_id=loan.book_id,
        borrowed_at=loan.borrowed_at,
        due_at=loan.due_at,
        returned_at=loan.returned_at,
        status=loan.status,
        fine=loan.fine
    )

@router.get("/{loan_id}", response_model=LoanResponse)
async def get_loan(
    loan_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific loan by ID."""
    loan = await get_loan_by_id(loan_id)
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    # Students can only see their own loans
    if current_user.role == "student" and loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    loan_response = LoanResponse(
        id=loan.id,
        user_id=loan.user_id,
        book_id=loan.book_id,
        borrowed_at=loan.borrowed_at,
        due_at=loan.due_at,
        returned_at=loan.returned_at,
        status=loan.status,
        fine=loan.fine
    )
    
    # Add user info for staff
    if current_user.role in ["admin", "librarian", "teacher"]:
        user = await get_user_by_id(loan.user_id)
        if user:
            loan_response.user = UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                class_name=user.class_name,
                phone=user.phone,
                active=user.active,
                created_at=user.created_at
            )
    
    # Add book info
    book = await get_book_by_id(loan.book_id)
    if book:
        loan_response.book = BookResponse(
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
    
    return loan_response