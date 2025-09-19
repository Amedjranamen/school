from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
from auth import get_current_user, require_role
from models import User
from database import books_collection, loans_collection, users_collection
from bson import ObjectId

def convert_objectid_to_str(data):
    """Convert ObjectId fields to strings for JSON serialization"""
    if isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/dashboard-stats")
async def get_dashboard_stats(
    current_user: User = Depends(require_role(["admin", "librarian"]))
):
    """Get comprehensive dashboard statistics"""
    
    # Basic counts
    total_books = await books_collection.count_documents({})
    total_users = await users_collection.count_documents({})
    active_loans = await loans_collection.count_documents({"status": "borrowed"})
    overdue_loans = await loans_collection.count_documents({"status": "overdue"})
    
    # Available books
    available_books_pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$available_copies"}}}
    ]
    available_books_result = await books_collection.aggregate(available_books_pipeline).to_list(1)
    available_books = available_books_result[0]["total"] if available_books_result else 0
    
    # Popular books this month
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    popular_books_pipeline = [
        {"$match": {"borrowed_at": {"$gte": one_month_ago}}},
        {"$group": {"_id": "$book_id", "loan_count": {"$sum": 1}}},
        {"$sort": {"loan_count": -1}},
        {"$limit": 5},
        {"$lookup": {
            "from": "books",
            "localField": "_id",
            "foreignField": "id",
            "as": "book_info"
        }},
        {"$unwind": "$book_info"},
        {"$project": {
            "book_title": "$book_info.title",
            "book_authors": "$book_info.authors",
            "loan_count": 1
        }}
    ]
    
    popular_books = await loans_collection.aggregate(popular_books_pipeline).to_list(5)
    
    # Recent activity (last 10 loans)
    recent_loans_pipeline = [
        {"$sort": {"borrowed_at": -1}},
        {"$limit": 10},
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
            "id": 1,
            "book_title": "$book_info.title",
            "user_name": "$user_info.full_name",
            "borrowed_at": 1,
            "due_at": 1,
            "status": 1
        }}
    ]
    
    recent_activity = await loans_collection.aggregate(recent_loans_pipeline).to_list(10)
    
    # Monthly loan statistics (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_stats_pipeline = [
        {"$match": {"borrowed_at": {"$gte": six_months_ago}}},
        {"$group": {
            "_id": {
                "year": {"$year": "$borrowed_at"},
                "month": {"$month": "$borrowed_at"}
            },
            "total_loans": {"$sum": 1},
            "returned_loans": {
                "$sum": {"$cond": [{"$ne": ["$returned_at", None]}, 1, 0]}
            }
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}},
        {"$project": {
            "month": {"$concat": [
                {"$toString": "$_id.year"}, 
                "-", 
                {"$toString": "$_id.month"}
            ]},
            "total_loans": 1,
            "returned_loans": 1,
            "active_loans": {"$subtract": ["$total_loans", "$returned_loans"]}
        }}
    ]
    
    monthly_stats = await loans_collection.aggregate(monthly_stats_pipeline).to_list(6)
    
    return {
        "overview": {
            "total_books": total_books,
            "available_books": available_books,
            "total_users": total_users,
            "active_loans": active_loans,
            "overdue_loans": overdue_loans
        },
        "popular_books": popular_books,
        "recent_activity": recent_activity,
        "monthly_stats": monthly_stats
    }

@router.get("/loans-report")
async def get_loans_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    user_role: Optional[str] = Query(None),
    current_user: User = Depends(require_role(["admin", "librarian"]))
):
    """Get detailed loans report with filters"""
    
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
    
    # Build aggregation pipeline
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
    ]
    
    # Add user role filter if specified
    if user_role:
        pipeline.append({"$match": {"user_info.role": user_role}})
    
    # Add projection
    pipeline.append({
        "$project": {
            "id": 1,
            "book_title": "$book_info.title",
            "book_authors": "$book_info.authors",
            "user_name": "$user_info.full_name",
            "user_role": "$user_info.role",
            "user_class": "$user_info.class",
            "borrowed_at": 1,
            "due_at": 1,
            "returned_at": 1,
            "status": 1,
            "fine": 1,
            "days_overdue": {
                "$cond": [
                    {"$eq": ["$status", "overdue"]},
                    {"$divide": [
                        {"$subtract": [datetime.utcnow(), "$due_at"]},
                        86400000  # milliseconds in a day
                    ]},
                    0
                ]
            }
        }
    })
    
    # Sort by borrowed date (newest first)
    pipeline.append({"$sort": {"borrowed_at": -1}})
    
    loans_report = await loans_collection.aggregate(pipeline).to_list(None)
    
    # Calculate summary statistics
    total_loans = len(loans_report)
    total_fines = sum(loan.get("fine", 0) for loan in loans_report)
    status_counts = {}
    
    for loan in loans_report:
        status = loan["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "summary": {
            "total_loans": total_loans,
            "total_fines": total_fines,
            "status_breakdown": status_counts
        },
        "loans": loans_report
    }

@router.get("/books-report")
async def get_books_report(
    category: Optional[str] = Query(None),
    availability: Optional[str] = Query(None),  # "available", "unavailable", "all"
    current_user: User = Depends(require_role(["admin", "librarian"]))
):
    """Get detailed books report with loan statistics"""
    
    # Build filter query
    filter_query = {}
    
    if category:
        filter_query["categories"] = {"$in": [category]}
    
    if availability == "available":
        filter_query["available_copies"] = {"$gt": 0}
    elif availability == "unavailable":
        filter_query["available_copies"] = 0
    
    # Aggregation pipeline to get books with loan statistics
    pipeline = [
        {"$match": filter_query},
        {"$lookup": {
            "from": "loans",
            "localField": "id",
            "foreignField": "book_id",
            "as": "loans"
        }},
        {"$addFields": {
            "total_loans": {"$size": "$loans"},
            "active_loans": {
                "$size": {
                    "$filter": {
                        "input": "$loans",
                        "cond": {"$in": ["$$this.status", ["borrowed", "overdue"]]}
                    }
                }
            },
            "popularity_score": {
                "$divide": [
                    {"$size": "$loans"},
                    {"$max": [1, "$total_copies"]}  # Avoid division by zero
                ]
            }
        }},
        {"$project": {
            "id": 1,
            "title": 1,
            "authors": 1,
            "isbn": 1,
            "publisher": 1,
            "year": 1,
            "categories": 1,
            "total_copies": 1,
            "available_copies": 1,
            "location": 1,
            "total_loans": 1,
            "active_loans": 1,
            "popularity_score": 1,
            "created_at": 1
        }},
        {"$sort": {"popularity_score": -1}}
    ]
    
    books_report = await books_collection.aggregate(pipeline).to_list(None)
    
    # Convert ObjectIds to strings for JSON serialization
    books_report = convert_objectid_to_str(books_report)
    
    # Calculate summary statistics
    total_books = len(books_report)
    total_copies = sum(book["total_copies"] for book in books_report)
    available_copies = sum(book["available_copies"] for book in books_report)
    total_loans_all_books = sum(book["total_loans"] for book in books_report)
    
    # Category statistics
    category_stats = {}
    for book in books_report:
        for cat in book.get("categories", []):
            if cat not in category_stats:
                category_stats[cat] = {"books": 0, "total_loans": 0}
            category_stats[cat]["books"] += 1
            category_stats[cat]["total_loans"] += book["total_loans"]
    
    return {
        "summary": {
            "total_books": total_books,
            "total_copies": total_copies,
            "available_copies": available_copies,
            "loan_rate": round((total_copies - available_copies) / max(total_copies, 1) * 100, 2),
            "total_historical_loans": total_loans_all_books
        },
        "category_stats": category_stats,
        "books": books_report
    }

@router.get("/users-report")
async def get_users_report(
    role: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    current_user: User = Depends(require_role(["admin", "librarian"]))
):
    """Get detailed users report with loan activity"""
    
    # Build filter query
    filter_query = {}
    
    if role:
        filter_query["role"] = role
    
    if class_name:
        filter_query["class"] = class_name
    
    # Aggregation pipeline
    pipeline = [
        {"$match": filter_query},
        {"$lookup": {
            "from": "loans",
            "localField": "id",
            "foreignField": "user_id",
            "as": "loans"
        }},
        {"$addFields": {
            "total_loans": {"$size": "$loans"},
            "active_loans": {
                "$size": {
                    "$filter": {
                        "input": "$loans",
                        "cond": {"$in": ["$$this.status", ["borrowed", "overdue"]]}
                    }
                }
            },
            "overdue_loans": {
                "$size": {
                    "$filter": {
                        "input": "$loans",
                        "cond": {"$eq": ["$$this.status", "overdue"]}
                    }
                }
            },
            "total_fines": {
                "$sum": "$loans.fine"
            },
            "last_loan_date": {"$max": "$loans.borrowed_at"}
        }},
        {"$project": {
            "id": 1,
            "username": 1,
            "full_name": 1,
            "email": 1,
            "role": 1,
            "class": 1,
            "active": 1,
            "created_at": 1,
            "total_loans": 1,
            "active_loans": 1,
            "overdue_loans": 1,
            "total_fines": 1,
            "last_loan_date": 1
        }},
        {"$sort": {"total_loans": -1}}
    ]
    
    users_report = await users_collection.aggregate(pipeline).to_list(None)
    
    # Calculate summary statistics
    total_users = len(users_report)
    active_users = sum(1 for user in users_report if user["active"])
    total_loans_all_users = sum(user["total_loans"] for user in users_report)
    total_fines_all_users = sum(user.get("total_fines", 0) for user in users_report)
    
    # Role statistics
    role_stats = {}
    for user in users_report:
        role = user["role"]
        if role not in role_stats:
            role_stats[role] = {"count": 0, "total_loans": 0}
        role_stats[role]["count"] += 1
        role_stats[role]["total_loans"] += user["total_loans"]
    
    return {
        "summary": {
            "total_users": total_users,
            "active_users": active_users,
            "total_loans": total_loans_all_users,
            "total_fines": total_fines_all_users,
            "avg_loans_per_user": round(total_loans_all_users / max(total_users, 1), 2)
        },
        "role_stats": role_stats,
        "users": users_report
    }