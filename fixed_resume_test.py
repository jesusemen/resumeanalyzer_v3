#!/usr/bin/env python3
"""
Fixed Protected Resume Analysis Test
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

def test_protected_resume_analysis():
    """Test the protected resume analysis endpoint"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🧪 Testing file type validation with authentication...")
    
    # Test 1: Invalid job description file type
    files = [
        ('job_description', ('job.txt', 'Software Engineer Job Description', 'text/plain')),
        ('resumes', ('resume1.txt', 'John Doe Resume', 'text/plain'))
    ]
    
    response = requests.post(f"{BACKEND_URL}/analyze-resumes", files=files, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 400:
        error_data = response.json()
        if "PDF, DOC, or DOCX" in error_data.get("detail", ""):
            print("✅ Job description file type validation working with authentication")
            return True
        else:
            print(f"❌ Unexpected error message: {error_data}")
            return False
    elif response.status_code == 422:
        # FastAPI validation error - let's check the details
        error_data = response.json()
        print(f"FastAPI validation error: {error_data}")
        
        # This might be due to the way we're sending files, let's try a different approach
        print("\n🧪 Trying alternative file upload format...")
        
        # Create file-like objects
        job_file = io.BytesIO(b'Software Engineer Job Description')
        resume_file = io.BytesIO(b'John Doe Resume')
        
        files = {
            'job_description': ('job.txt', job_file, 'text/plain'),
            'resumes': ('resume1.txt', resume_file, 'text/plain')
        }
        
        response = requests.post(f"{BACKEND_URL}/analyze-resumes", files=files, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            error_data = response.json()
            if "PDF, DOC, or DOCX" in error_data.get("detail", ""):
                print("✅ Job description file type validation working with authentication")
                return True
        
        return False
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Protected Resume Analysis Endpoint")
    print("=" * 50)
    
    success = test_protected_resume_analysis()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Protected resume analysis validation test passed!")
    else:
        print("⚠️ Protected resume analysis validation test needs investigation")
    
    exit(0 if success else 1)