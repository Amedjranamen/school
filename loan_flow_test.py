#!/usr/bin/env python3
"""
Focused test for loan creation and return flow
"""

import requests
import json
from datetime import datetime

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

def test_loan_flow():
    """Test complete loan flow"""
    print("=== TESTING COMPLETE LOAN FLOW ===")
    
    # Login as admin and student
    admin_token = login("admin", "admin123")
    student_token = login("eleve_sophie", "eleve123")
    
    if not admin_token or not student_token:
        print("❌ Failed to login")
        return False
    
    # Get student user ID
    response = make_request("GET", "/auth/me", token=student_token)
    if response.status_code != 200:
        print("❌ Failed to get student profile")
        return False
    
    student_id = response.json()["id"]
    print(f"✅ Student ID: {student_id}")
    
    # Get available books
    response = make_request("GET", "/books/", token=admin_token, params={"available": True})
    if response.status_code != 200:
        print("❌ Failed to get books")
        return False
    
    books = response.json()
    available_books = [book for book in books if book["available_copies"] > 0]
    
    if not available_books:
        print("❌ No available books")
        return False
    
    book = available_books[0]
    print(f"✅ Selected book: {book['title']} (Available: {book['available_copies']})")
    
    # Create loan
    loan_data = {
        "user_id": student_id,
        "book_id": book["id"],
        "due_days": 14
    }
    
    response = make_request("POST", "/loans/", token=admin_token, data=loan_data)
    if response.status_code != 200:
        print(f"❌ Failed to create loan: {response.status_code} - {response.text}")
        return False
    
    loan = response.json()
    loan_id = loan["id"]
    print(f"✅ Loan created: {loan_id}")
    print(f"   Due date: {loan['due_at']}")
    
    # Verify book availability decreased
    response = make_request("GET", f"/books/{book['id']}", token=admin_token)
    if response.status_code == 200:
        updated_book = response.json()
        expected_copies = book["available_copies"] - 1
        if updated_book["available_copies"] == expected_copies:
            print(f"✅ Book availability updated: {updated_book['available_copies']} (was {book['available_copies']})")
        else:
            print(f"❌ Book availability not updated correctly: {updated_book['available_copies']} (expected {expected_copies})")
    
    # Check student can see their loan
    response = make_request("GET", "/loans/my", token=student_token)
    if response.status_code == 200:
        student_loans = response.json()
        if len(student_loans) > 0 and student_loans[0]["id"] == loan_id:
            print(f"✅ Student can see their loan")
        else:
            print(f"❌ Student cannot see their loan")
    
    # Return the book
    response = make_request("PUT", f"/loans/{loan_id}/return", token=admin_token)
    if response.status_code != 200:
        print(f"❌ Failed to return book: {response.status_code} - {response.text}")
        return False
    
    returned_loan = response.json()
    print(f"✅ Book returned successfully")
    print(f"   Status: {returned_loan['status']}")
    print(f"   Fine: {returned_loan['fine']}")
    
    # Verify book availability increased
    response = make_request("GET", f"/books/{book['id']}", token=admin_token)
    if response.status_code == 200:
        final_book = response.json()
        if final_book["available_copies"] == book["available_copies"]:
            print(f"✅ Book availability restored: {final_book['available_copies']}")
        else:
            print(f"❌ Book availability not restored: {final_book['available_copies']} (expected {book['available_copies']})")
    
    print("✅ Complete loan flow test passed!")
    return True

if __name__ == "__main__":
    success = test_loan_flow()
    exit(0 if success else 1)