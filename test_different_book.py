#!/usr/bin/env python3
"""
Test loan with different book
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
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data)
    
    return response

def test_with_different_book():
    """Test loan with different book"""
    print("=== TESTING LOAN WITH DIFFERENT BOOK ===")
    
    # Login as admin and different student
    admin_token = login("admin", "admin123")
    student_token = login("eleve_pierre", "eleve123")  # Different student
    
    if not admin_token or not student_token:
        print("❌ Failed to login")
        return False
    
    # Get student user ID
    response = make_request("GET", "/auth/me", token=student_token)
    student_id = response.json()["id"]
    print(f"✅ Student ID: {student_id}")
    
    # Get available books
    response = make_request("GET", "/books/", token=admin_token)
    if response.status_code != 200:
        print("❌ Failed to get books")
        return False
    
    books = response.json()
    available_books = [book for book in books if book["available_copies"] > 0]
    
    if len(available_books) < 2:
        print("❌ Need at least 2 available books")
        return False
    
    # Use the second book to avoid conflicts
    book = available_books[1]
    print(f"✅ Selected book: {book['title']} (Available: {book['available_copies']})")
    
    # Create loan
    loan_data = {
        "user_id": student_id,
        "book_id": book["id"],
        "due_days": 7
    }
    
    response = make_request("POST", "/loans/", token=admin_token, data=loan_data)
    if response.status_code != 200:
        print(f"❌ Failed to create loan: {response.status_code} - {response.text}")
        return False
    
    loan = response.json()
    loan_id = loan["id"]
    print(f"✅ Loan created: {loan_id}")
    print(f"   Due date: {loan['due_at']}")
    
    # Return the book immediately
    response = make_request("PUT", f"/loans/{loan_id}/return", token=admin_token)
    if response.status_code != 200:
        print(f"❌ Failed to return book: {response.status_code} - {response.text}")
        return False
    
    returned_loan = response.json()
    print(f"✅ Book returned successfully")
    print(f"   Status: {returned_loan['status']}")
    print(f"   Fine: {returned_loan['fine']}")
    
    return True

if __name__ == "__main__":
    success = test_with_different_book()
    exit(0 if success else 1)