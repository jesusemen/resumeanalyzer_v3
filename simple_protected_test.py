#!/usr/bin/env python3
"""
Simplified Protected Resume Analysis Test
Tests the key authentication and validation aspects
"""

import requests
import json
import io

# Get backend URL from environment
BACKEND_URL = "https://84b26680-6501-4b17-abb8-460652a5c606.preview.emergentagent.com/api"

def get_auth_token():
    """Get authentication token"""
    try:
        login_data = {
            "email": "testuser@example.com",
            "password": "securepassword123"
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def test_simplified_protected_resume_analysis():
    """Test key aspects of the protected resume analysis endpoint"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    test_results = []
    
    # Test 1: Invalid job description file type with authentication
    print("🧪 Test 1: Invalid job description file type with authentication...")
    
    job_file = io.BytesIO(b'Software Engineer Job Description')
    resume_file = io.BytesIO(b'John Doe Resume')
    
    files = {
        'job_description': ('job.txt', job_file, 'text/plain'),
        'resumes': ('resume1.txt', resume_file, 'text/plain')
    }
    
    response = requests.post(f"{BACKEND_URL}/analyze-resumes", files=files, headers=headers)
    
    if response.status_code == 400:
        error_data = response.json()
        if "PDF, DOC, or DOCX" in error_data.get("detail", ""):
            print("✅ Job description file type validation working with authentication")
            test_results.append(True)
        else:
            print(f"❌ Unexpected error message: {error_data}")
            test_results.append(False)
    else:
        print(f"❌ Expected 400, got {response.status_code}: {response.text}")
        test_results.append(False)
    
    # Test 2: Resume count validation with valid file types
    print("\n🧪 Test 2: Resume count validation with valid file types...")
    
    # Create a simple PDF-like content
    pdf_content = b'%PDF-1.4\nSimple PDF content for testing'
    
    job_file = io.BytesIO(pdf_content)
    resume_file = io.BytesIO(pdf_content)
    
    files = {
        'job_description': ('job.pdf', job_file, 'application/pdf'),
        'resumes': ('resume1.pdf', resume_file, 'application/pdf')
    }
    
    response = requests.post(f"{BACKEND_URL}/analyze-resumes", files=files, headers=headers)
    
    if response.status_code == 400:
        error_data = response.json()
        if "30 resumes" in error_data.get("detail", ""):
            print("✅ Resume count validation working with authentication")
            test_results.append(True)
        else:
            print(f"❌ Unexpected error message: {error_data}")
            test_results.append(False)
    else:
        print(f"❌ Expected 400, got {response.status_code}: {response.text}")
        test_results.append(False)
    
    return all(test_results)

if __name__ == "__main__":
    print("🚀 Testing Simplified Protected Resume Analysis Endpoint")
    print("=" * 60)
    
    success = test_simplified_protected_resume_analysis()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Protected resume analysis validation tests passed!")
        print("✅ Authentication is working correctly")
        print("✅ File type validation is working correctly")
        print("✅ Resume count validation is working correctly")
    else:
        print("⚠️ Some protected resume analysis validation tests failed")
    
    exit(0 if success else 1)