#!/usr/bin/env python3
"""
Focused test for Reports API endpoints - specifically testing the failing endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://biblioschool-1.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}

def get_admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_CREDENTIALS, timeout=30)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Failed to get admin token: {response.status_code} - {response.text}")
        return None

def test_reports_endpoints():
    """Test all reports endpoints with detailed error capture"""
    print("=== FOCUSED REPORTS API TESTING ===")
    print(f"Base URL: {BASE_URL}")
    print(f"Testing with admin credentials")
    print()
    
    # Get admin token
    token = get_admin_token()
    if not token:
        print("❌ Cannot proceed without admin token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test endpoints
    endpoints = [
        ("/reports/dashboard-stats", "Dashboard Stats"),
        ("/reports/loans-report", "Loans Report"),
        ("/reports/books-report", "Books Report"),
        ("/reports/users-report", "Users Report")
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        print(f"Testing {name} ({endpoint})...")
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=30)
            
            print(f"  Status Code: {response.status_code}")
            print(f"  Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  ✅ SUCCESS: {name}")
                    print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, (list, dict)):
                                print(f"    {key}: {type(value).__name__} with {len(value) if hasattr(value, '__len__') else 'N/A'} items")
                            else:
                                print(f"    {key}: {value}")
                    results[endpoint] = {"status": "SUCCESS", "data": data}
                except json.JSONDecodeError as e:
                    print(f"  ❌ JSON Decode Error: {e}")
                    print(f"  Raw response: {response.text[:500]}...")
                    results[endpoint] = {"status": "JSON_ERROR", "error": str(e), "raw": response.text}
            else:
                print(f"  ❌ FAILED: {name}")
                print(f"  Error response: {response.text}")
                results[endpoint] = {"status": "HTTP_ERROR", "code": response.status_code, "error": response.text}
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ REQUEST ERROR: {e}")
            results[endpoint] = {"status": "REQUEST_ERROR", "error": str(e)}
        
        print()
    
    # Summary
    print("=== SUMMARY ===")
    for endpoint, result in results.items():
        status = result["status"]
        if status == "SUCCESS":
            print(f"✅ {endpoint}: Working")
        else:
            print(f"❌ {endpoint}: {status}")
            if "error" in result:
                print(f"   Error: {result['error'][:200]}...")
    
    return results

if __name__ == "__main__":
    test_reports_endpoints()