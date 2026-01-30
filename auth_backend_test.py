#!/usr/bin/env python3
"""
Authentication Backend Test Suite
Tests the new authentication features added to the resume analyzer backend
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://84b26680-6501-4b17-abb8-460652a5c606.preview.emergentagent.com/api"

class AuthBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_user_email = "testuser@example.com"
        self.test_user_password = "securepassword123"
        self.test_user_name = "Test User"
        self.access_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Resume Analyzer API Ready":
                    self.log_test("Health Check", True, "API is responding correctly")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        try:
            # First, try to register a new user
            user_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "full_name": self.test_user_name
            }
            
            response = requests.post(f"{self.base_url}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.access_token = data["access_token"]
                    user_info = data["user"]
                    if (user_info["email"] == self.test_user_email and 
                        user_info["full_name"] == self.test_user_name):
                        self.log_test("User Registration", True, "User registered successfully with valid token")
                        return True
                    else:
                        self.log_test("User Registration", False, "User info mismatch in response")
                        return False
                else:
                    self.log_test("User Registration", False, f"Missing token or user in response: {data}")
                    return False
            elif response.status_code == 400:
                # User might already exist, try to continue with login
                error_data = response.json()
                if "already registered" in error_data.get("detail", "").lower():
                    self.log_test("User Registration", True, "User already exists (expected for repeated tests)")
                    return True
                else:
                    self.log_test("User Registration", False, f"Registration failed: {error_data}")
                    return False
            else:
                self.log_test("User Registration", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Registration", False, f"Request error: {str(e)}")
            return False
    
    def test_user_login_valid(self):
        """Test user login with valid credentials"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.access_token = data["access_token"]
                    user_info = data["user"]
                    if (user_info["email"] == self.test_user_email and 
                        user_info["full_name"] == self.test_user_name):
                        self.log_test("User Login (Valid)", True, "Login successful with valid credentials")
                        return True
                    else:
                        self.log_test("User Login (Valid)", False, "User info mismatch in login response")
                        return False
                else:
                    self.log_test("User Login (Valid)", False, f"Missing token or user in response: {data}")
                    return False
            else:
                self.log_test("User Login (Valid)", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Login (Valid)", False, f"Request error: {str(e)}")
            return False
    
    def test_user_login_invalid(self):
        """Test user login with invalid credentials"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": "wrongpassword123"
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 401:
                data = response.json()
                if "invalid" in data.get("detail", "").lower():
                    self.log_test("User Login (Invalid)", True, "Correctly rejected invalid credentials")
                    return True
                else:
                    self.log_test("User Login (Invalid)", False, f"Unexpected error message: {data}")
                    return False
            else:
                self.log_test("User Login (Invalid)", False, f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Login (Invalid)", False, f"Request error: {str(e)}")
            return False
    
    def test_protected_profile_with_token(self):
        """Test protected profile endpoint with valid token"""
        if not self.access_token:
            self.log_test("Profile (With Token)", False, "No access token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.base_url}/user/profile", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("email") == self.test_user_email and 
                    data.get("full_name") == self.test_user_name):
                    self.log_test("Profile (With Token)", True, "Profile retrieved successfully with valid token")
                    return True
                else:
                    self.log_test("Profile (With Token)", False, f"Profile data mismatch: {data}")
                    return False
            else:
                self.log_test("Profile (With Token)", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile (With Token)", False, f"Request error: {str(e)}")
            return False
    
    def test_protected_profile_without_token(self):
        """Test protected profile endpoint without token"""
        try:
            response = requests.get(f"{self.base_url}/user/profile")
            
            if response.status_code == 403:
                self.log_test("Profile (Without Token)", True, "Correctly rejected request without token")
                return True
            elif response.status_code == 401:
                self.log_test("Profile (Without Token)", True, "Correctly rejected request without token (401)")
                return True
            else:
                self.log_test("Profile (Without Token)", False, f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Profile (Without Token)", False, f"Request error: {str(e)}")
            return False
    
    def test_protected_resume_analysis_without_token(self):
        """Test protected resume analysis endpoint without token"""
        try:
            # Create a simple test file
            files = {
                'job_description': ('job.txt', 'Software Engineer Job Description', 'text/plain'),
                'resumes': ('resume.txt', 'John Doe Resume', 'text/plain')
            }
            
            response = requests.post(f"{self.base_url}/analyze-resumes", files=files)
            
            if response.status_code == 403:
                self.log_test("Resume Analysis (Without Token)", True, "Correctly rejected request without token")
                return True
            elif response.status_code == 401:
                self.log_test("Resume Analysis (Without Token)", True, "Correctly rejected request without token (401)")
                return True
            else:
                self.log_test("Resume Analysis (Without Token)", False, f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Resume Analysis (Without Token)", False, f"Request error: {str(e)}")
            return False
    
    def test_protected_analysis_history_with_token(self):
        """Test protected analysis history endpoint with valid token"""
        if not self.access_token:
            self.log_test("Analysis History (With Token)", False, "No access token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.base_url}/analysis-history", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Analysis History (With Token)", True, f"Analysis history retrieved successfully ({len(data)} records)")
                    return True
                else:
                    self.log_test("Analysis History (With Token)", False, f"Expected list, got: {type(data)}")
                    return False
            else:
                self.log_test("Analysis History (With Token)", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Analysis History (With Token)", False, f"Request error: {str(e)}")
            return False
    
    def test_token_verification(self):
        """Test JWT token verification"""
        if not self.access_token:
            self.log_test("Token Verification", False, "No access token available")
            return False
        
        try:
            # Test with valid token
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.base_url}/user/profile", headers=headers)
            
            if response.status_code == 200:
                # Test with invalid token
                invalid_headers = {"Authorization": "Bearer invalid_token_here"}
                invalid_response = requests.get(f"{self.base_url}/user/profile", headers=invalid_headers)
                
                if invalid_response.status_code == 401:
                    self.log_test("Token Verification", True, "Valid token accepted, invalid token rejected")
                    return True
                else:
                    self.log_test("Token Verification", False, f"Invalid token not rejected properly: {invalid_response.status_code}")
                    return False
            else:
                self.log_test("Token Verification", False, f"Valid token not accepted: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Token Verification", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting Authentication Backend Tests")
        print("=" * 50)
        
        tests = [
            self.test_health_check,
            self.test_user_registration,
            self.test_user_login_valid,
            self.test_user_login_invalid,
            self.test_protected_profile_with_token,
            self.test_protected_profile_without_token,
            self.test_protected_resume_analysis_without_token,
            self.test_protected_analysis_history_with_token,
            self.test_token_verification
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All authentication tests passed!")
        else:
            print(f"⚠️  {total - passed} tests failed")
        
        return passed == total

if __name__ == "__main__":
    tester = AuthBackendTester()
    success = tester.run_all_tests()
    
    # Print detailed results
    print("\n" + "=" * 50)
    print("📋 Detailed Test Results:")
    for result in tester.test_results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}: {result['message']}")
    
    exit(0 if success else 1)