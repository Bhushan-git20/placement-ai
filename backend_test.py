#!/usr/bin/env python3
"""
Backend API Testing Script for Placement-AI
Tests all backend endpoints and functionality
"""

import requests
import json
import uuid
from datetime import datetime
import sys
import os

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("❌ Could not determine backend URL")
    sys.exit(1)

API_BASE = f"{BASE_URL}/api"
print(f"🔗 Testing backend at: {API_BASE}")

def test_hello_world():
    """Test GET /api/ endpoint"""
    print("\n🧪 Testing GET /api/ endpoint...")
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "Hello World":
                print("✅ GET /api/ endpoint working correctly")
                return True
            else:
                print(f"❌ Unexpected response: {data}")
                return False
        else:
            print(f"❌ GET /api/ failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GET /api/ failed with error: {e}")
        return False

def test_post_status():
    """Test POST /api/status endpoint"""
    print("\n🧪 Testing POST /api/status endpoint...")
    
    test_data = {
        "client_name": "TestClient_PlacementAI"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/status", 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            # Validate response structure
            required_fields = ["id", "client_name", "timestamp"]
            if all(field in data for field in required_fields):
                if data["client_name"] == test_data["client_name"]:
                    print("✅ POST /api/status endpoint working correctly")
                    return True, data
                else:
                    print(f"❌ Client name mismatch: expected {test_data['client_name']}, got {data['client_name']}")
                    return False, None
            else:
                print(f"❌ Missing required fields in response: {data}")
                return False, None
        else:
            print(f"❌ POST /api/status failed with status {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ POST /api/status failed with error: {e}")
        return False, None

def test_get_status():
    """Test GET /api/status endpoint"""
    print("\n🧪 Testing GET /api/status endpoint...")
    try:
        response = requests.get(f"{API_BASE}/status", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ GET /api/status endpoint working correctly - returned {len(data)} records")
                # Validate structure of returned items
                if data:
                    first_item = data[0]
                    required_fields = ["id", "client_name", "timestamp"]
                    if all(field in first_item for field in required_fields):
                        print("✅ Response structure is valid")
                        return True, data
                    else:
                        print(f"❌ Invalid response structure: {first_item}")
                        return False, None
                else:
                    print("✅ Empty list returned (no data yet)")
                    return True, data
            else:
                print(f"❌ Expected list, got: {type(data)}")
                return False, None
        else:
            print(f"❌ GET /api/status failed with status {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ GET /api/status failed with error: {e}")
        return False, None

def test_cors():
    """Test CORS functionality"""
    print("\n🧪 Testing CORS functionality...")
    try:
        # Test preflight request
        response = requests.options(
            f"{API_BASE}/status",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        print(f"CORS Preflight Status Code: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
        # Check for CORS headers
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers"
        ]
        
        has_cors = any(header in response.headers for header in cors_headers)
        if has_cors:
            print("✅ CORS headers present")
            return True
        else:
            print("❌ CORS headers missing")
            return False
    except Exception as e:
        print(f"❌ CORS test failed with error: {e}")
        return False

def test_mongodb_integration():
    """Test MongoDB integration by creating and retrieving data"""
    print("\n🧪 Testing MongoDB integration...")
    
    # Create a unique test record
    unique_client = f"MongoTest_{uuid.uuid4().hex[:8]}"
    
    # Step 1: Create a record
    print(f"Creating test record with client_name: {unique_client}")
    success, created_record = test_post_status_with_data({"client_name": unique_client})
    
    if not success:
        print("❌ Failed to create test record for MongoDB test")
        return False
    
    # Step 2: Retrieve records and verify our record exists
    print("Retrieving all records to verify MongoDB storage...")
    success, all_records = test_get_status()
    
    if not success:
        print("❌ Failed to retrieve records for MongoDB test")
        return False
    
    # Step 3: Check if our record exists
    found_record = None
    for record in all_records:
        if record.get("client_name") == unique_client:
            found_record = record
            break
    
    if found_record:
        print(f"✅ MongoDB integration working - record found: {found_record}")
        return True
    else:
        print(f"❌ MongoDB integration failed - record not found in {len(all_records)} records")
        return False

def test_post_status_with_data(data):
    """Helper function to test POST with specific data"""
    try:
        response = requests.post(
            f"{API_BASE}/status", 
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, None
    except Exception as e:
        print(f"Error in POST request: {e}")
        return False, None

def test_data_validation():
    """Test Pydantic model validation"""
    print("\n🧪 Testing data validation...")
    
    # Test with missing required field
    print("Testing with missing client_name...")
    try:
        response = requests.post(
            f"{API_BASE}/status", 
            json={},  # Missing client_name
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 422:  # Validation error
            print("✅ Validation working correctly - rejected invalid data")
            return True
        else:
            print(f"❌ Expected validation error (422), got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Validation test failed with error: {e}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print("🚀 Starting Backend API Tests for Placement-AI")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: Hello World endpoint
    test_results["hello_world"] = test_hello_world()
    
    # Test 2: POST status endpoint
    test_results["post_status"] = test_post_status()[0]
    
    # Test 3: GET status endpoint
    test_results["get_status"] = test_get_status()[0]
    
    # Test 4: CORS functionality
    test_results["cors"] = test_cors()
    
    # Test 5: MongoDB integration
    test_results["mongodb"] = test_mongodb_integration()
    
    # Test 6: Data validation
    test_results["validation"] = test_data_validation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)