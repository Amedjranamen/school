#!/usr/bin/env python3
"""
Comprehensive authentication test to verify the exact issue with demo accounts
"""

import requests
import json

BASE_URL = "https://biblioschool-1.preview.emergentagent.com/api"

def test_comprehensive_auth():
    print("🔍 COMPREHENSIVE AUTHENTICATION ANALYSIS")
    print("="*60)
    
    # Test 1: Verify what the frontend is showing vs what works
    print("\n1️⃣ FRONTEND DEMO ACCOUNTS (from Login.js):")
    frontend_accounts = [
        {"email": "admin@ecole.fr", "password": "admin123", "role": "Administrateur"},
        {"email": "bibliothecaire@ecole.fr", "password": "biblio123", "role": "Bibliothécaire"},
        {"email": "prof.martin@ecole.fr", "password": "prof123", "role": "Enseignant"},
        {"email": "eleve.sophie@ecole.fr", "password": "eleve123", "role": "Élève"}
    ]
    
    for account in frontend_accounts:
        print(f"   📧 {account['role']}: {account['email']} / {account['password']}")
    
    print("\n2️⃣ BACKEND SEEDED ACCOUNTS (from seed_data.py):")
    backend_accounts = [
        {"username": "admin", "email": "admin@ecole.fr", "password": "admin123", "role": "admin"},
        {"username": "bibliothecaire", "email": "bibliothecaire@ecole.fr", "password": "biblio123", "role": "librarian"},
        {"username": "prof_martin", "email": "martin@ecole.fr", "password": "prof123", "role": "teacher"},
        {"username": "eleve_sophie", "email": "sophie@ecole.fr", "password": "eleve123", "role": "student"},
        {"username": "eleve_pierre", "email": "pierre@ecole.fr", "password": "eleve123", "role": "student"}
    ]
    
    for account in backend_accounts:
        print(f"   👤 {account['role']}: {account['username']} (email: {account['email']}) / {account['password']}")
    
    print("\n3️⃣ TESTING FRONTEND DEMO ACCOUNTS (using emails as username):")
    working_frontend = []
    for account in frontend_accounts:
        success = test_login_attempt(account['email'], account['password'], f"Frontend {account['role']}")
        if success:
            working_frontend.append(account)
    
    print("\n4️⃣ TESTING BACKEND ACCOUNTS (using actual usernames):")
    working_backend = []
    for account in backend_accounts:
        success = test_login_attempt(account['username'], account['password'], f"Backend {account['role']}")
        if success:
            working_backend.append(account)
    
    print("\n5️⃣ TESTING EMAIL-TO-USERNAME MAPPING:")
    # Test if we can map frontend emails to backend usernames
    email_to_username_map = {
        "admin@ecole.fr": "admin",
        "bibliothecaire@ecole.fr": "bibliothecaire", 
        "prof.martin@ecole.fr": "prof_martin",  # Note: frontend has dot, backend has underscore
        "eleve.sophie@ecole.fr": "eleve_sophie"  # Note: frontend has dot, backend has underscore
    }
    
    working_mapped = []
    for frontend_email, backend_username in email_to_username_map.items():
        # Find the password from frontend accounts
        password = None
        for fa in frontend_accounts:
            if fa['email'] == frontend_email:
                password = fa['password']
                break
        
        if password:
            success = test_login_attempt(backend_username, password, f"Mapped {frontend_email} -> {backend_username}")
            if success:
                working_mapped.append((frontend_email, backend_username))
    
    # Summary
    print("\n" + "="*60)
    print("📊 ANALYSIS SUMMARY:")
    print(f"   Frontend demo accounts working: {len(working_frontend)}/4")
    print(f"   Backend seeded accounts working: {len(working_backend)}/5") 
    print(f"   Email-to-username mapping working: {len(working_mapped)}/4")
    
    print("\n🔧 ROOT CAUSE IDENTIFIED:")
    if len(working_frontend) == 0 and len(working_backend) > 0:
        print("   ❌ Frontend shows EMAIL ADDRESSES but backend expects USERNAMES")
        print("   ❌ Email addresses in frontend don't match usernames in backend")
        print("   ❌ Some frontend emails have DOTS (prof.martin) but backend has UNDERSCORES (prof_martin)")
        
        print("\n💡 SOLUTIONS:")
        print("   1. Update frontend demo accounts to show correct usernames")
        print("   2. OR modify backend to accept email addresses for login")
        print("   3. OR create proper email-to-username mapping in frontend")
        
        print("\n✅ WORKING CREDENTIALS (for user reference):")
        for account in working_backend:
            print(f"   - {account['username']} / {account['password']} ({account['role']})")
    
    return len(working_frontend), len(working_backend), len(working_mapped)

def test_login_attempt(username, password, description):
    """Test a single login attempt"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            print(f"   ✅ {description}: SUCCESS - {user.get('full_name')} ({user.get('role')})")
            return True
        else:
            error = response.json().get('detail', 'Unknown error')
            print(f"   ❌ {description}: FAILED - {error}")
            return False
            
    except Exception as e:
        print(f"   ❌ {description}: ERROR - {str(e)}")
        return False

if __name__ == "__main__":
    test_comprehensive_auth()