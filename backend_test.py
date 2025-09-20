#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for School Library Management System
Tests all authentication, books, and loans endpoints with role-based access control.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Optional

# Configuration
BASE_URL = "https://biblioschool-2.preview.emergentagent.com/api"

# Test accounts with CORRECT usernames (not emails)
TEST_ACCOUNTS = {
    "admin": {"username": "admin", "password": "admin123"},
    "librarian": {"username": "bibliothecaire", "password": "biblio123"},
    "teacher": {"username": "prof_martin", "password": "prof123"},
    "student1": {"username": "eleve_sophie", "password": "eleve123"},
    "student2": {"username": "eleve_pierre", "password": "eleve123"}
}

class LibraryAPITester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.created_books = []
        self.created_loans = []
        
    def log_result(self, test_name: str, success: bool, message: str = "", details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if message:
            print(f"    Message: {message}")
        if details and not success:
            print(f"    Details: {details}")
        print()

    def make_request(self, method: str, endpoint: str, token: str = None, data: dict = None, params: dict = None) -> tuple:
        """Make HTTP request with proper headers"""
        url = f"{BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, f"Unsupported method: {method}"
            
            return True, response
        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}"

    def test_authentication_flow(self):
        """Test complete authentication flow for all user roles"""
        print("=== TESTING AUTHENTICATION FLOW ===")
        
        # Test login for each account
        for role, credentials in TEST_ACCOUNTS.items():
            success, response = self.make_request("POST", "/auth/login", data=credentials)
            
            if not success:
                self.log_result(f"Auth Login - {role}", False, f"Request failed: {response}")
                continue
                
            if response.status_code == 200:
                try:
                    token_data = response.json()
                    if "access_token" in token_data and "user" in token_data:
                        self.tokens[role] = token_data["access_token"]
                        user_info = token_data["user"]
                        expected_role = "librarian" if role == "librarian" else role.replace("1", "").replace("2", "")
                        if role.startswith("student"):
                            expected_role = "student"
                        elif role == "teacher":
                            expected_role = "teacher"
                        
                        if user_info["role"] == expected_role:
                            self.log_result(f"Auth Login - {role}", True, f"Successfully logged in as {expected_role}")
                        else:
                            self.log_result(f"Auth Login - {role}", False, f"Role mismatch: expected {expected_role}, got {user_info['role']}")
                    else:
                        self.log_result(f"Auth Login - {role}", False, "Missing access_token or user in response")
                except json.JSONDecodeError:
                    self.log_result(f"Auth Login - {role}", False, "Invalid JSON response")
            else:
                self.log_result(f"Auth Login - {role}", False, f"HTTP {response.status_code}: {response.text}")

        # Test /auth/me endpoint for each logged-in user
        for role, token in self.tokens.items():
            success, response = self.make_request("GET", "/auth/me", token=token)
            
            if not success:
                self.log_result(f"Auth Profile - {role}", False, f"Request failed: {response}")
                continue
                
            if response.status_code == 200:
                try:
                    user_data = response.json()
                    if "username" in user_data and "role" in user_data:
                        self.log_result(f"Auth Profile - {role}", True, f"Profile retrieved for {user_data['username']}")
                    else:
                        self.log_result(f"Auth Profile - {role}", False, "Missing user data in response")
                except json.JSONDecodeError:
                    self.log_result(f"Auth Profile - {role}", False, "Invalid JSON response")
            else:
                self.log_result(f"Auth Profile - {role}", False, f"HTTP {response.status_code}: {response.text}")

    def test_books_crud_operations(self):
        """Test Books CRUD operations with role-based access"""
        print("=== TESTING BOOKS CRUD OPERATIONS ===")
        
        # Test GET /books (should work for all authenticated users)
        for role, token in self.tokens.items():
            success, response = self.make_request("GET", "/books/", token=token)
            
            if not success:
                self.log_result(f"Books List - {role}", False, f"Request failed: {response}")
                continue
                
            if response.status_code == 200:
                try:
                    books = response.json()
                    if isinstance(books, list):
                        self.log_result(f"Books List - {role}", True, f"Retrieved {len(books)} books")
                    else:
                        self.log_result(f"Books List - {role}", False, "Response is not a list")
                except json.JSONDecodeError:
                    self.log_result(f"Books List - {role}", False, "Invalid JSON response")
            else:
                self.log_result(f"Books List - {role}", False, f"HTTP {response.status_code}: {response.text}")

        # Test book search functionality
        if "admin" in self.tokens:
            success, response = self.make_request("GET", "/books/", token=self.tokens["admin"], params={"search": "Python"})
            
            if success and response.status_code == 200:
                self.log_result("Books Search", True, "Search functionality working")
            else:
                self.log_result("Books Search", False, f"Search failed: {response.status_code if success else response}")

        # Test POST /books (should only work for librarian/admin)
        test_book = {
            "title": "Test Book for API Testing",
            "authors": ["Test Author"],
            "isbn": "978-0123456789",
            "publisher": "Test Publisher",
            "year": 2024,
            "description": "A book created for API testing purposes",
            "categories": ["Technology", "Testing"],
            "location": "Section A, Shelf 1",
            "tags": ["test", "api"],
            "total_copies": 3
        }

        # Test with admin (should succeed)
        if "admin" in self.tokens:
            success, response = self.make_request("POST", "/books/", token=self.tokens["admin"], data=test_book)
            
            if not success:
                self.log_result("Books Create - Admin", False, f"Request failed: {response}")
            elif response.status_code == 200:
                try:
                    created_book = response.json()
                    if "id" in created_book:
                        self.created_books.append(created_book["id"])
                        self.log_result("Books Create - Admin", True, f"Book created with ID: {created_book['id']}")
                    else:
                        self.log_result("Books Create - Admin", False, "No ID in created book response")
                except json.JSONDecodeError:
                    self.log_result("Books Create - Admin", False, "Invalid JSON response")
            else:
                self.log_result("Books Create - Admin", False, f"HTTP {response.status_code}: {response.text}")

        # Test with librarian (should succeed)
        if "librarian" in self.tokens:
            librarian_book = test_book.copy()
            librarian_book["title"] = "Librarian Test Book"
            success, response = self.make_request("POST", "/books/", token=self.tokens["librarian"], data=librarian_book)
            
            if not success:
                self.log_result("Books Create - Librarian", False, f"Request failed: {response}")
            elif response.status_code == 200:
                try:
                    created_book = response.json()
                    if "id" in created_book:
                        self.created_books.append(created_book["id"])
                        self.log_result("Books Create - Librarian", True, f"Book created with ID: {created_book['id']}")
                    else:
                        self.log_result("Books Create - Librarian", False, "No ID in created book response")
                except json.JSONDecodeError:
                    self.log_result("Books Create - Librarian", False, "Invalid JSON response")
            else:
                self.log_result("Books Create - Librarian", False, f"HTTP {response.status_code}: {response.text}")

        # Test with student (should fail)
        if "student1" in self.tokens:
            student_book = test_book.copy()
            student_book["title"] = "Student Test Book"
            success, response = self.make_request("POST", "/books/", token=self.tokens["student1"], data=student_book)
            
            if not success:
                self.log_result("Books Create - Student (Should Fail)", False, f"Request failed: {response}")
            elif response.status_code == 403:
                self.log_result("Books Create - Student (Should Fail)", True, "Correctly denied access to student")
            else:
                self.log_result("Books Create - Student (Should Fail)", False, f"Expected 403, got {response.status_code}")

        # Test GET /books/{id} for created books
        if self.created_books and "admin" in self.tokens:
            book_id = self.created_books[0]
            success, response = self.make_request("GET", f"/books/{book_id}", token=self.tokens["admin"])
            
            if not success:
                self.log_result("Books Get by ID", False, f"Request failed: {response}")
            elif response.status_code == 200:
                try:
                    book_data = response.json()
                    if book_data.get("id") == book_id:
                        self.log_result("Books Get by ID", True, f"Retrieved book: {book_data['title']}")
                    else:
                        self.log_result("Books Get by ID", False, "Book ID mismatch")
                except json.JSONDecodeError:
                    self.log_result("Books Get by ID", False, "Invalid JSON response")
            else:
                self.log_result("Books Get by ID", False, f"HTTP {response.status_code}: {response.text}")

        # Test PUT /books/{id} (update book)
        if self.created_books and "admin" in self.tokens:
            book_id = self.created_books[0]
            update_data = {"description": "Updated description for testing"}
            success, response = self.make_request("PUT", f"/books/{book_id}", token=self.tokens["admin"], data=update_data)
            
            if not success:
                self.log_result("Books Update", False, f"Request failed: {response}")
            elif response.status_code == 200:
                try:
                    updated_book = response.json()
                    if updated_book.get("description") == "Updated description for testing":
                        self.log_result("Books Update", True, "Book successfully updated")
                    else:
                        self.log_result("Books Update", False, "Book update not reflected")
                except json.JSONDecodeError:
                    self.log_result("Books Update", False, "Invalid JSON response")
            else:
                self.log_result("Books Update", False, f"HTTP {response.status_code}: {response.text}")

    def test_loans_operations(self):
        """Test Loans operations with role-based access"""
        print("=== TESTING LOANS OPERATIONS ===")
        
        # First, get available books
        available_books = []
        if "admin" in self.tokens:
            success, response = self.make_request("GET", "/books", token=self.tokens["admin"], params={"available": True})
            if success and response.status_code == 200:
                try:
                    books = response.json()
                    available_books = [book for book in books if book.get("available_copies", 0) > 0]
                except json.JSONDecodeError:
                    pass

        # Get user IDs for loan creation
        user_ids = {}
        for role, token in self.tokens.items():
            success, response = self.make_request("GET", "/auth/me", token=token)
            if success and response.status_code == 200:
                try:
                    user_data = response.json()
                    user_ids[role] = user_data["id"]
                except json.JSONDecodeError:
                    pass

        # Test POST /loans (create loan) - should only work for staff
        if available_books and "student1" in user_ids and "admin" in self.tokens:
            loan_data = {
                "user_id": user_ids["student1"],
                "book_id": available_books[0]["id"],
                "due_days": 14
            }
            
            success, response = self.make_request("POST", "/loans/", token=self.tokens["admin"], data=loan_data)
            
            if not success:
                self.log_result("Loans Create - Admin", False, f"Request failed: {response}")
            elif response.status_code == 200:
                try:
                    created_loan = response.json()
                    if "id" in created_loan:
                        self.created_loans.append(created_loan["id"])
                        self.log_result("Loans Create - Admin", True, f"Loan created with ID: {created_loan['id']}")
                    else:
                        self.log_result("Loans Create - Admin", False, "No ID in created loan response")
                except json.JSONDecodeError:
                    self.log_result("Loans Create - Admin", False, "Invalid JSON response")
            else:
                self.log_result("Loans Create - Admin", False, f"HTTP {response.status_code}: {response.text}")

        # Test with student (should fail)
        if available_books and "student2" in user_ids and "student1" in self.tokens:
            loan_data = {
                "user_id": user_ids["student2"],
                "book_id": available_books[0]["id"] if len(available_books) > 0 else "dummy-id",
                "due_days": 14
            }
            
            success, response = self.make_request("POST", "/loans/", token=self.tokens["student1"], data=loan_data)
            
            if not success:
                self.log_result("Loans Create - Student (Should Fail)", False, f"Request failed: {response}")
            elif response.status_code == 403:
                self.log_result("Loans Create - Student (Should Fail)", True, "Correctly denied access to student")
            else:
                self.log_result("Loans Create - Student (Should Fail)", False, f"Expected 403, got {response.status_code}")

        # Test GET /loans (list loans)
        for role, token in self.tokens.items():
            success, response = self.make_request("GET", "/loans/", token=token)
            
            if not success:
                self.log_result(f"Loans List - {role}", False, f"Request failed: {response}")
                continue
                
            if response.status_code == 200:
                try:
                    loans = response.json()
                    if isinstance(loans, list):
                        self.log_result(f"Loans List - {role}", True, f"Retrieved {len(loans)} loans")
                    else:
                        self.log_result(f"Loans List - {role}", False, "Response is not a list")
                except json.JSONDecodeError:
                    self.log_result(f"Loans List - {role}", False, "Invalid JSON response")
            else:
                self.log_result(f"Loans List - {role}", False, f"HTTP {response.status_code}: {response.text}")

        # Test GET /loans/my (user's own loans)
        for role, token in self.tokens.items():
            success, response = self.make_request("GET", "/loans/my", token=token)
            
            if not success:
                self.log_result(f"Loans My - {role}", False, f"Request failed: {response}")
                continue
                
            if response.status_code == 200:
                try:
                    loans = response.json()
                    if isinstance(loans, list):
                        self.log_result(f"Loans My - {role}", True, f"Retrieved {len(loans)} personal loans")
                    else:
                        self.log_result(f"Loans My - {role}", False, "Response is not a list")
                except json.JSONDecodeError:
                    self.log_result(f"Loans My - {role}", False, "Invalid JSON response")
            else:
                self.log_result(f"Loans My - {role}", False, f"HTTP {response.status_code}: {response.text}")

        # Test GET /loans/{id} for created loans
        if self.created_loans and "admin" in self.tokens:
            loan_id = self.created_loans[0]
            success, response = self.make_request("GET", f"/loans/{loan_id}", token=self.tokens["admin"])
            
            if not success:
                self.log_result("Loans Get by ID", False, f"Request failed: {response}")
            elif response.status_code == 200:
                try:
                    loan_data = response.json()
                    if loan_data.get("id") == loan_id:
                        self.log_result("Loans Get by ID", True, f"Retrieved loan: {loan_id}")
                    else:
                        self.log_result("Loans Get by ID", False, "Loan ID mismatch")
                except json.JSONDecodeError:
                    self.log_result("Loans Get by ID", False, "Invalid JSON response")
            else:
                self.log_result("Loans Get by ID", False, f"HTTP {response.status_code}: {response.text}")

        # Test PUT /loans/{id}/return (return book)
        if self.created_loans and "admin" in self.tokens:
            loan_id = self.created_loans[0]
            success, response = self.make_request("PUT", f"/loans/{loan_id}/return", token=self.tokens["admin"])
            
            if not success:
                self.log_result("Loans Return", False, f"Request failed: {response}")
            elif response.status_code == 200:
                try:
                    returned_loan = response.json()
                    if returned_loan.get("status") == "returned":
                        self.log_result("Loans Return", True, "Book successfully returned")
                    else:
                        self.log_result("Loans Return", False, f"Expected status 'returned', got '{returned_loan.get('status')}'")
                except json.JSONDecodeError:
                    self.log_result("Loans Return", False, "Invalid JSON response")
            else:
                self.log_result("Loans Return", False, f"HTTP {response.status_code}: {response.text}")

    def test_role_based_permissions(self):
        """Test role-based access control across different endpoints"""
        print("=== TESTING ROLE-BASED PERMISSIONS ===")
        
        # Test scenarios where students should be denied access
        restricted_endpoints = [
            ("POST", "/books/", {"title": "Test", "authors": ["Test"], "total_copies": 1}),
        ]
        
        for method, endpoint, data in restricted_endpoints:
            if "student1" in self.tokens:
                success, response = self.make_request(method, endpoint, token=self.tokens["student1"], data=data)
                
                if not success:
                    self.log_result(f"Permission Test - Student {method} {endpoint}", False, f"Request failed: {response}")
                elif response.status_code == 403:
                    self.log_result(f"Permission Test - Student {method} {endpoint}", True, "Correctly denied access")
                else:
                    self.log_result(f"Permission Test - Student {method} {endpoint}", False, f"Expected 403, got {response.status_code}")

    def test_users_management_apis(self):
        """Test User Management CRUD APIs"""
        print("=== TESTING USER MANAGEMENT APIs ===")
        
        # Test GET /users (list with pagination and filters) - Admin/Librarian only
        for role in ["admin", "librarian"]:
            if role in self.tokens:
                success, response = self.make_request("GET", "/users/", token=self.tokens[role])
                
                if not success:
                    self.log_result(f"Users List - {role}", False, f"Request failed: {response}")
                elif response.status_code == 200:
                    try:
                        users = response.json()
                        if isinstance(users, list):
                            self.log_result(f"Users List - {role}", True, f"Retrieved {len(users)} users")
                        else:
                            self.log_result(f"Users List - {role}", False, "Response is not a list")
                    except json.JSONDecodeError:
                        self.log_result(f"Users List - {role}", False, "Invalid JSON response")
                else:
                    self.log_result(f"Users List - {role}", False, f"HTTP {response.status_code}: {response.text}")

        # Test with student (should fail)
        if "student1" in self.tokens:
            success, response = self.make_request("GET", "/users/", token=self.tokens["student1"])
            if success and response.status_code == 403:
                self.log_result("Users List - Student (Should Fail)", True, "Correctly denied access to student")
            else:
                self.log_result("Users List - Student (Should Fail)", False, f"Expected 403, got {response.status_code if success else 'request failed'}")

        # Test GET /users/stats - Admin/Librarian only
        for role in ["admin", "librarian"]:
            if role in self.tokens:
                success, response = self.make_request("GET", "/users/stats", token=self.tokens[role])
                
                if not success:
                    self.log_result(f"Users Stats - {role}", False, f"Request failed: {response}")
                elif response.status_code == 200:
                    try:
                        stats = response.json()
                        if "total_users" in stats and "users_by_role" in stats:
                            self.log_result(f"Users Stats - {role}", True, f"Retrieved user statistics: {stats['total_users']} total users")
                        else:
                            self.log_result(f"Users Stats - {role}", False, "Missing required fields in stats response")
                    except json.JSONDecodeError:
                        self.log_result(f"Users Stats - {role}", False, "Invalid JSON response")
                else:
                    self.log_result(f"Users Stats - {role}", False, f"HTTP {response.status_code}: {response.text}")

        # Test POST /users (create user) - Admin only
        if "admin" in self.tokens:
            test_user = {
                "username": "test_user_api",
                "email": "test.user@ecole.fr",
                "password": "testpass123",
                "full_name": "Test User API",
                "role": "student",
                "class_name": "6ème B",
                "phone": "0123456789"
            }
            
            success, response = self.make_request("POST", "/users/", token=self.tokens["admin"], data=test_user)
            
            if not success:
                self.log_result("Users Create - Admin", False, f"Request failed: {response}")
            elif response.status_code == 200:
                try:
                    created_user = response.json()
                    if "id" in created_user and created_user["username"] == test_user["username"]:
                        self.created_users = getattr(self, 'created_users', [])
                        self.created_users.append(created_user["id"])
                        self.log_result("Users Create - Admin", True, f"User created with ID: {created_user['id']}")
                    else:
                        self.log_result("Users Create - Admin", False, "Invalid user creation response")
                except json.JSONDecodeError:
                    self.log_result("Users Create - Admin", False, "Invalid JSON response")
            else:
                self.log_result("Users Create - Admin", False, f"HTTP {response.status_code}: {response.text}")

        # Test with librarian (should fail)
        if "librarian" in self.tokens:
            test_user_lib = {
                "username": "test_user_lib",
                "email": "test.lib@ecole.fr",
                "password": "testpass123",
                "full_name": "Test User Lib",
                "role": "student"
            }
            
            success, response = self.make_request("POST", "/users/", token=self.tokens["librarian"], data=test_user_lib)
            if success and response.status_code == 403:
                self.log_result("Users Create - Librarian (Should Fail)", True, "Correctly denied access to librarian")
            else:
                self.log_result("Users Create - Librarian (Should Fail)", False, f"Expected 403, got {response.status_code if success else 'request failed'}")

        # Test GET /users/{user_id} - Admin/Librarian only
        if hasattr(self, 'created_users') and self.created_users and "admin" in self.tokens:
            user_id = self.created_users[0]
            success, response = self.make_request("GET", f"/users/{user_id}", token=self.tokens["admin"])
            
            if not success:
                self.log_result("Users Get by ID", False, f"Request failed: {response}")
            elif response.status_code == 200:
                try:
                    user_data = response.json()
                    if user_data.get("id") == user_id:
                        self.log_result("Users Get by ID", True, f"Retrieved user: {user_data['full_name']}")
                    else:
                        self.log_result("Users Get by ID", False, "User ID mismatch")
                except json.JSONDecodeError:
                    self.log_result("Users Get by ID", False, "Invalid JSON response")
            else:
                self.log_result("Users Get by ID", False, f"HTTP {response.status_code}: {response.text}")

        # Test PUT /users/{user_id} (update user) - Admin only
        if hasattr(self, 'created_users') and self.created_users and "admin" in self.tokens:
            user_id = self.created_users[0]
            update_data = {"full_name": "Updated Test User", "phone": "0987654321"}
            success, response = self.make_request("PUT", f"/users/{user_id}", token=self.tokens["admin"], data=update_data)
            
            if not success:
                self.log_result("Users Update", False, f"Request failed: {response}")
            elif response.status_code == 200:
                try:
                    updated_user = response.json()
                    if updated_user.get("full_name") == "Updated Test User":
                        self.log_result("Users Update", True, "User successfully updated")
                    else:
                        self.log_result("Users Update", False, "User update not reflected")
                except json.JSONDecodeError:
                    self.log_result("Users Update", False, "Invalid JSON response")
            else:
                self.log_result("Users Update", False, f"HTTP {response.status_code}: {response.text}")

    def test_reports_apis(self):
        """Test Reports and Statistics APIs"""
        print("=== TESTING REPORTS APIs ===")
        
        # Test GET /reports/dashboard-stats - Admin/Librarian only
        for role in ["admin", "librarian"]:
            if role in self.tokens:
                success, response = self.make_request("GET", "/reports/dashboard-stats", token=self.tokens[role])
                
                if not success:
                    self.log_result(f"Dashboard Stats - {role}", False, f"Request failed: {response}")
                elif response.status_code == 200:
                    try:
                        stats = response.json()
                        if "overview" in stats and "popular_books" in stats:
                            overview = stats["overview"]
                            self.log_result(f"Dashboard Stats - {role}", True, f"Retrieved dashboard stats: {overview.get('total_books', 0)} books, {overview.get('total_users', 0)} users")
                        else:
                            self.log_result(f"Dashboard Stats - {role}", False, "Missing required fields in dashboard stats")
                    except json.JSONDecodeError:
                        self.log_result(f"Dashboard Stats - {role}", False, "Invalid JSON response")
                else:
                    self.log_result(f"Dashboard Stats - {role}", False, f"HTTP {response.status_code}: {response.text}")

        # Test GET /reports/loans-report - Admin/Librarian only
        for role in ["admin", "librarian"]:
            if role in self.tokens:
                success, response = self.make_request("GET", "/reports/loans-report", token=self.tokens[role])
                
                if not success:
                    self.log_result(f"Loans Report - {role}", False, f"Request failed: {response}")
                elif response.status_code == 200:
                    try:
                        report = response.json()
                        if "summary" in report and "loans" in report:
                            summary = report["summary"]
                            self.log_result(f"Loans Report - {role}", True, f"Retrieved loans report: {summary.get('total_loans', 0)} loans")
                        else:
                            self.log_result(f"Loans Report - {role}", False, "Missing required fields in loans report")
                    except json.JSONDecodeError:
                        self.log_result(f"Loans Report - {role}", False, "Invalid JSON response")
                else:
                    self.log_result(f"Loans Report - {role}", False, f"HTTP {response.status_code}: {response.text}")

        # Test GET /reports/books-report - Admin/Librarian only
        for role in ["admin", "librarian"]:
            if role in self.tokens:
                success, response = self.make_request("GET", "/reports/books-report", token=self.tokens[role])
                
                if not success:
                    self.log_result(f"Books Report - {role}", False, f"Request failed: {response}")
                elif response.status_code == 200:
                    try:
                        report = response.json()
                        if "summary" in report and "books" in report:
                            summary = report["summary"]
                            self.log_result(f"Books Report - {role}", True, f"Retrieved books report: {summary.get('total_books', 0)} books")
                        else:
                            self.log_result(f"Books Report - {role}", False, "Missing required fields in books report")
                    except json.JSONDecodeError:
                        self.log_result(f"Books Report - {role}", False, "Invalid JSON response")
                else:
                    self.log_result(f"Books Report - {role}", False, f"HTTP {response.status_code}: {response.text}")

        # Test GET /reports/users-report - Admin/Librarian only
        for role in ["admin", "librarian"]:
            if role in self.tokens:
                success, response = self.make_request("GET", "/reports/users-report", token=self.tokens[role])
                
                if not success:
                    self.log_result(f"Users Report - {role}", False, f"Request failed: {response}")
                elif response.status_code == 200:
                    try:
                        report = response.json()
                        if "summary" in report and "users" in report:
                            summary = report["summary"]
                            self.log_result(f"Users Report - {role}", True, f"Retrieved users report: {summary.get('total_users', 0)} users")
                        else:
                            self.log_result(f"Users Report - {role}", False, "Missing required fields in users report")
                    except json.JSONDecodeError:
                        self.log_result(f"Users Report - {role}", False, "Invalid JSON response")
                else:
                    self.log_result(f"Users Report - {role}", False, f"HTTP {response.status_code}: {response.text}")

        # Test with student (should fail for all reports)
        if "student1" in self.tokens:
            report_endpoints = ["/reports/dashboard-stats", "/reports/loans-report", "/reports/books-report", "/reports/users-report"]
            for endpoint in report_endpoints:
                success, response = self.make_request("GET", endpoint, token=self.tokens["student1"])
                if success and response.status_code == 403:
                    self.log_result(f"Reports {endpoint} - Student (Should Fail)", True, "Correctly denied access to student")
                else:
                    self.log_result(f"Reports {endpoint} - Student (Should Fail)", False, f"Expected 403, got {response.status_code if success else 'request failed'}")

    def test_import_export_apis(self):
        """Test Import/Export CSV APIs"""
        print("=== TESTING IMPORT/EXPORT APIs ===")
        
        # Test GET /import-export/template/books (CSV template)
        if "admin" in self.tokens:
            success, response = self.make_request("GET", "/import-export/template/books", token=self.tokens["admin"])
            
            if not success:
                self.log_result("Books Template - Admin", False, f"Request failed: {response}")
            elif response.status_code == 200:
                if response.headers.get("content-type") == "text/csv; charset=utf-8":
                    self.log_result("Books Template - Admin", True, "Books CSV template downloaded successfully")
                else:
                    self.log_result("Books Template - Admin", False, f"Expected CSV content-type, got {response.headers.get('content-type')}")
            else:
                self.log_result("Books Template - Admin", False, f"HTTP {response.status_code}: {response.text}")

        # Test GET /import-export/template/users (CSV template) - Admin only
        if "admin" in self.tokens:
            success, response = self.make_request("GET", "/import-export/template/users", token=self.tokens["admin"])
            
            if not success:
                self.log_result("Users Template - Admin", False, f"Request failed: {response}")
            elif response.status_code == 200:
                if response.headers.get("content-type") == "text/csv; charset=utf-8":
                    self.log_result("Users Template - Admin", True, "Users CSV template downloaded successfully")
                else:
                    self.log_result("Users Template - Admin", False, f"Expected CSV content-type, got {response.headers.get('content-type')}")
            else:
                self.log_result("Users Template - Admin", False, f"HTTP {response.status_code}: {response.text}")

        # Test GET /import-export/books/export - Admin/Librarian only
        for role in ["admin", "librarian"]:
            if role in self.tokens:
                success, response = self.make_request("GET", "/import-export/books/export", token=self.tokens[role])
                
                if not success:
                    self.log_result(f"Books Export - {role}", False, f"Request failed: {response}")
                elif response.status_code == 200:
                    if response.headers.get("content-type") == "text/csv; charset=utf-8":
                        self.log_result(f"Books Export - {role}", True, "Books exported successfully")
                    else:
                        self.log_result(f"Books Export - {role}", False, f"Expected CSV content-type, got {response.headers.get('content-type')}")
                else:
                    self.log_result(f"Books Export - {role}", False, f"HTTP {response.status_code}: {response.text}")

        # Test GET /import-export/users/export - Admin only
        if "admin" in self.tokens:
            success, response = self.make_request("GET", "/import-export/users/export", token=self.tokens["admin"])
            
            if not success:
                self.log_result("Users Export - Admin", False, f"Request failed: {response}")
            elif response.status_code == 200:
                if response.headers.get("content-type") == "text/csv; charset=utf-8":
                    self.log_result("Users Export - Admin", True, "Users exported successfully")
                else:
                    self.log_result("Users Export - Admin", False, f"Expected CSV content-type, got {response.headers.get('content-type')}")
            else:
                self.log_result("Users Export - Admin", False, f"HTTP {response.status_code}: {response.text}")

        # Test GET /import-export/loans/export - Admin/Librarian only
        for role in ["admin", "librarian"]:
            if role in self.tokens:
                success, response = self.make_request("GET", "/import-export/loans/export", token=self.tokens[role])
                
                if not success:
                    self.log_result(f"Loans Export - {role}", False, f"Request failed: {response}")
                elif response.status_code == 200:
                    if response.headers.get("content-type") == "text/csv; charset=utf-8":
                        self.log_result(f"Loans Export - {role}", True, "Loans exported successfully")
                    else:
                        self.log_result(f"Loans Export - {role}", False, f"Expected CSV content-type, got {response.headers.get('content-type')}")
                else:
                    self.log_result(f"Loans Export - {role}", False, f"HTTP {response.status_code}: {response.text}")

        # Test with student (should fail for export endpoints)
        if "student1" in self.tokens:
            export_endpoints = ["/import-export/books/export", "/import-export/users/export", "/import-export/loans/export"]
            for endpoint in export_endpoints:
                success, response = self.make_request("GET", endpoint, token=self.tokens["student1"])
                if success and response.status_code == 403:
                    self.log_result(f"Export {endpoint} - Student (Should Fail)", True, "Correctly denied access to student")
                else:
                    self.log_result(f"Export {endpoint} - Student (Should Fail)", False, f"Expected 403, got {response.status_code if success else 'request failed'}")

        # Test POST /users/bulk-import - Admin only
        if "admin" in self.tokens:
            bulk_users = [
                {
                    "username": "bulk_user1",
                    "email": "bulk1@ecole.fr",
                    "password": "bulk123",
                    "full_name": "Bulk User 1",
                    "role": "student",
                    "class_name": "5ème A"
                },
                {
                    "username": "bulk_user2",
                    "email": "bulk2@ecole.fr",
                    "password": "bulk123",
                    "full_name": "Bulk User 2",
                    "role": "student",
                    "class_name": "5ème B"
                }
            ]
            
            success, response = self.make_request("POST", "/users/bulk-import", token=self.tokens["admin"], data=bulk_users)
            
            if not success:
                self.log_result("Users Bulk Import - Admin", False, f"Request failed: {response}")
            elif response.status_code == 200:
                try:
                    result = response.json()
                    if "created" in result and result["created"] >= 0:
                        self.log_result("Users Bulk Import - Admin", True, f"Bulk import completed: {result['created']} users created")
                    else:
                        self.log_result("Users Bulk Import - Admin", False, "Invalid bulk import response")
                except json.JSONDecodeError:
                    self.log_result("Users Bulk Import - Admin", False, "Invalid JSON response")
            else:
                self.log_result("Users Bulk Import - Admin", False, f"HTTP {response.status_code}: {response.text}")

    def test_business_rules(self):
        """Test business logic and validation rules"""
        print("=== TESTING BUSINESS RULES ===")
        
        # Test that users cannot borrow the same book twice
        if "admin" in self.tokens and "student1" in self.tokens:
            # Get user ID
            success, response = self.make_request("GET", "/auth/me", token=self.tokens["student1"])
            if success and response.status_code == 200:
                try:
                    user_data = response.json()
                    user_id = user_data["id"]
                    
                    # Get available books
                    success, response = self.make_request("GET", "/books/", token=self.tokens["admin"], params={"available": True})
                    if success and response.status_code == 200:
                        books = response.json()
                        if books:
                            book_id = books[0]["id"]
                            
                            # Create first loan
                            loan_data = {"user_id": user_id, "book_id": book_id, "due_days": 14}
                            success, response = self.make_request("POST", "/loans/", token=self.tokens["admin"], data=loan_data)
                            
                            if success and response.status_code == 200:
                                # Try to create second loan for same book
                                success2, response2 = self.make_request("POST", "/loans/", token=self.tokens["admin"], data=loan_data)
                                
                                if success2 and response2.status_code == 400:
                                    self.log_result("Business Rule - Duplicate Loan Prevention", True, "Correctly prevented duplicate loan")
                                else:
                                    self.log_result("Business Rule - Duplicate Loan Prevention", False, f"Expected 400, got {response2.status_code if success2 else 'request failed'}")
                            else:
                                self.log_result("Business Rule - Duplicate Loan Prevention", False, "Could not create initial loan for testing")
                except json.JSONDecodeError:
                    self.log_result("Business Rule - Duplicate Loan Prevention", False, "Invalid JSON response")

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("=== CLEANING UP TEST DATA ===")
        
        # Delete created users (only if we have admin access)
        if "admin" in self.tokens and hasattr(self, 'created_users'):
            for user_id in self.created_users:
                success, response = self.make_request("DELETE", f"/users/{user_id}", token=self.tokens["admin"])
                if success and response.status_code == 200:
                    self.log_result(f"Cleanup - Delete User {user_id}", True, "User deleted successfully")
                else:
                    self.log_result(f"Cleanup - Delete User {user_id}", False, f"Failed to delete user: {response.status_code if success else 'request failed'}")
        
        # Delete created books (only if we have admin access)
        if "admin" in self.tokens:
            for book_id in self.created_books:
                success, response = self.make_request("DELETE", f"/books/{book_id}", token=self.tokens["admin"])
                if success and response.status_code == 200:
                    self.log_result(f"Cleanup - Delete Book {book_id}", True, "Book deleted successfully")
                else:
                    self.log_result(f"Cleanup - Delete Book {book_id}", False, f"Failed to delete book: {response.status_code if success else 'request failed'}")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print(f"\nFAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['message']}")
        
        print("\n" + "="*60)
        return failed_tests == 0

    def run_all_tests(self):
        """Run all test suites"""
        print("Starting comprehensive backend API testing...")
        print(f"Base URL: {BASE_URL}")
        print(f"Test Accounts: {list(TEST_ACCOUNTS.keys())}")
        print()
        
        try:
            # Run test suites in order
            self.test_authentication_flow()
            self.test_books_crud_operations()
            self.test_loans_operations()
            self.test_users_management_apis()
            self.test_reports_apis()
            self.test_import_export_apis()
            self.test_role_based_permissions()
            self.test_business_rules()
            self.cleanup_test_data()
            
            # Print final summary
            success = self.print_summary()
            return success
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR during testing: {str(e)}")
            return False

def main():
    """Main function to run tests"""
    tester = LibraryAPITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()