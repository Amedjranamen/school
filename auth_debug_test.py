#!/usr/bin/env python3
"""
Debug authentication issues with demo accounts
"""

import requests
import json

BASE_URL = "https://biblioschool-2.preview.emergentagent.com/api"

# Test accounts from seed_data.py
DEMO_ACCOUNTS = [
    {"username": "admin", "password": "admin123"},
    {"username": "bibliothecaire", "password": "biblio123"},
    {"username": "prof_martin", "password": "prof123"},
    {"username": "eleve_sophie", "password": "eleve123"},
    {"username": "eleve_pierre", "password": "eleve123"}
]

# Also test with email addresses (in case frontend is using emails)
EMAIL_ACCOUNTS = [
    {"username": "admin@ecole.fr", "password": "admin123"},
    {"username": "bibliothecaire@ecole.fr", "password": "biblio123"},
    {"username": "martin@ecole.fr", "password": "prof123"},
    {"username": "sophie@ecole.fr", "password": "eleve123"},
    {"username": "pierre@ecole.fr", "password": "eleve123"}
]

def test_login(credentials, account_type):
    """Test login with given credentials"""
    print(f"\n🔐 Testing {account_type}: {credentials['username']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=credentials,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                user = data.get("user", {})
                print(f"   ✅ SUCCESS - Logged in as: {user.get('full_name')} ({user.get('role')})")
                print(f"   📧 Email: {user.get('email')}")
                print(f"   🆔 Username: {user.get('username')}")
                return True, data.get("access_token")
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON response")
                return False, None
        else:
            try:
                error = response.json()
                print(f"   ❌ FAILED - {error.get('detail', 'Unknown error')}")
            except:
                print(f"   ❌ FAILED - HTTP {response.status_code}: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ REQUEST FAILED: {str(e)}")
        return False, None

def test_profile(token, username):
    """Test /auth/me endpoint"""
    print(f"\n👤 Testing profile for {username}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            user = response.json()
            print(f"   ✅ Profile retrieved: {user.get('full_name')} ({user.get('role')})")
            return True
        else:
            print(f"   ❌ Profile failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Profile request failed: {str(e)}")
        return False

def main():
    print("🔍 DEBUGGING AUTHENTICATION ISSUES")
    print(f"🌐 Base URL: {BASE_URL}")
    print("="*60)
    
    successful_logins = []
    
    # Test with usernames
    print("\n📝 TESTING WITH USERNAMES:")
    for credentials in DEMO_ACCOUNTS:
        success, token = test_login(credentials, "Username")
        if success and token:
            successful_logins.append((credentials["username"], token))
    
    # Test with emails
    print("\n📧 TESTING WITH EMAIL ADDRESSES:")
    for credentials in EMAIL_ACCOUNTS:
        success, token = test_login(credentials, "Email")
        if success and token:
            successful_logins.append((credentials["username"], token))
    
    # Test profiles for successful logins
    if successful_logins:
        print("\n" + "="*60)
        print("🎯 TESTING PROFILES FOR SUCCESSFUL LOGINS:")
        for username, token in successful_logins:
            test_profile(token, username)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY:")
    print(f"   Successful logins: {len(successful_logins)}")
    if successful_logins:
        print("   Working accounts:")
        for username, _ in successful_logins:
            print(f"     - {username}")
    else:
        print("   ❌ NO ACCOUNTS WORKING!")
        print("\n🔧 POSSIBLE ISSUES:")
        print("   1. Demo data not seeded properly")
        print("   2. Password hashing issue")
        print("   3. Database connection problem")
        print("   4. Authentication logic error")

if __name__ == "__main__":
    main()