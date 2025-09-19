#!/usr/bin/env python3
"""
Debug loan issues
"""

import requests
import json

BASE_URL = "https://bookflow-21.preview.emergentagent.com/api"

def login(username, password):
    """Login and get token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def make_request(method, endpoint, token=None, data=None, params=None):
    """Make authenticated request"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if method == "GET":
        response = requests.get(url, headers=headers, params=params)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    
    return response

def debug_loans():
    """Debug loan issues"""
    print("=== DEBUGGING LOAN ISSUES ===")
    
    # Login as admin
    admin_token = login("admin", "admin123")
    student_token = login("eleve_sophie", "eleve123")
    
    if not admin_token:
        print("❌ Failed to login as admin")
        return
    
    # Get student info
    response = make_request("GET", "/auth/me", token=student_token)
    student = response.json()
    student_id = student["id"]
    print(f"Student ID: {student_id}")
    
    # Check all loans
    response = make_request("GET", "/loans/", token=admin_token)
    if response.status_code == 200:
        all_loans = response.json()
        print(f"Total loans in system: {len(all_loans)}")
        
        student_loans = [loan for loan in all_loans if loan["user_id"] == student_id]
        print(f"Student's loans: {len(student_loans)}")
        
        for loan in student_loans:
            print(f"  Loan {loan['id']}: Book {loan['book_id']}, Status: {loan['status']}")
    
    # Check available books
    response = make_request("GET", "/books/", token=admin_token, params={"available": True})
    if response.status_code == 200:
        books = response.json()
        available_books = [book for book in books if book["available_copies"] > 0]
        print(f"Available books: {len(available_books)}")
        
        if available_books:
            book = available_books[0]
            print(f"First available book: {book['title']} (ID: {book['id']}, Available: {book['available_copies']})")
            
            # Try to create loan with this book
            loan_data = {
                "user_id": student_id,
                "book_id": book["id"],
                "due_days": 14
            }
            
            response = make_request("POST", "/loans/", token=admin_token, data=loan_data)
            print(f"Loan creation attempt: {response.status_code}")
            if response.status_code != 200:
                print(f"Error: {response.text}")
            else:
                print(f"Success: {response.json()}")

if __name__ == "__main__":
    debug_loans()