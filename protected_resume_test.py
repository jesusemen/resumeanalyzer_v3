#!/usr/bin/env python3
"""
Protected Resume Analysis Test
Tests the resume analysis endpoint with authentication
"""

import requests
import json
import io
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://84b26680-6501-4b17-abb8-460652a5c606.preview.emergentagent.com/api"

class ProtectedResumeAnalysisTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_user_email = "testuser@example.com"
        self.test_user_password = "securepassword123"
        self.access_token = None
        
    def get_auth_token(self):
        """Get authentication token"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_resume_analysis_validation_with_auth(self):
        """Test resume analysis validation with authentication"""
        if not self.access_token:
            print("❌ No authentication token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Test 1: Invalid file type for job description
            print("\n🧪 Testing job description file type validation...")
            files = {
                'job_description': ('job.txt', 'Software Engineer Job Description', 'text/plain')
            }
            
            response = requests.post(f"{self.base_url}/analyze-resumes", files=files, headers=headers)
            
            if response.status_code == 400:
                error_data = response.json()
                if "PDF, DOC, or DOCX" in error_data.get("detail", ""):
                    print("✅ Job description file type validation working")
                else:
                    print(f"❌ Unexpected error message: {error_data}")
                    return False
            else:
                print(f"❌ Expected 400, got {response.status_code}")
                return False
            
            # Test 2: Insufficient resume count
            print("\n🧪 Testing resume count validation...")
            
            # Create a mock PDF-like file (just for testing validation)
            job_content = b"%PDF-1.4\nFake PDF content for testing"
            files = {
                'job_description': ('job.pdf', job_content, 'application/pdf'),
                'resumes': [
                    ('resume1.pdf', job_content, 'application/pdf'),
                    ('resume2.pdf', job_content, 'application/pdf')
                ]
            }
            
            response = requests.post(f"{self.base_url}/analyze-resumes", files=files, headers=headers)
            
            if response.status_code == 400:
                error_data = response.json()
                if "30 resumes" in error_data.get("detail", ""):
                    print("✅ Resume count validation working")
                    return True
                else:
                    print(f"❌ Unexpected error message: {error_data}")
                    return False
            else:
                print(f"❌ Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return False
    
    def run_test(self):
        """Run the protected resume analysis test"""
        print("🚀 Starting Protected Resume Analysis Test")
        print("=" * 50)
        
        if not self.get_auth_token():
            return False
        
        success = self.test_resume_analysis_validation_with_auth()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Protected resume analysis test passed!")
        else:
            print("⚠️ Protected resume analysis test failed!")
        
        return success

if __name__ == "__main__":
    tester = ProtectedResumeAnalysisTest()
    success = tester.run_test()
    exit(0 if success else 1)