#!/usr/bin/env python3
"""
Debug Protected Resume Analysis Test
"""

import requests
import json

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

def debug_resume_analysis():
    """Debug the resume analysis endpoint"""
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with minimal valid request structure
    print("🧪 Testing with text file (should fail validation)...")
    files = {
        'job_description': ('job.txt', 'Software Engineer Job Description', 'text/plain')
    }
    
    response = requests.post(f"{BACKEND_URL}/analyze-resumes", files=files, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test with proper structure but invalid file type
    print("\n🧪 Testing with proper structure but invalid file type...")
    files = {
        'job_description': ('job.txt', 'Software Engineer Job Description', 'text/plain'),
        'resumes': [('resume1.txt', 'John Doe Resume', 'text/plain')]
    }
    
    response = requests.post(f"{BACKEND_URL}/analyze-resumes", files=files, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    debug_resume_analysis()