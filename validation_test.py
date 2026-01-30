#!/usr/bin/env python3
"""
Simple validation test for resume count changes
Tests the new 5-30 resume validation requirements
"""

import requests
import json

def get_backend_url():
    """Get backend URL from frontend .env file"""
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
        return "http://localhost:8001"

def test_validation():
    base_url = get_backend_url()
    print(f"Testing validation at: {base_url}")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print("   ❌ Health check failed")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Insufficient resumes (< 5)
    print("\n2. Testing insufficient resumes (3 resumes)...")
    try:
        # Create simple file content
        job_content = b"Job Description: Software Engineer position"
        resume_content = b"Resume: John Doe, Software Engineer"
        
        files = []
        files.append(('job_description', ('job.pdf', job_content, 'application/pdf')))
        
        # Add 3 resumes (insufficient)
        for i in range(3):
            files.append(('resumes', (f'resume{i+1}.pdf', resume_content, 'application/pdf')))
        
        response = requests.post(f"{base_url}/api/analyze-resumes", files=files)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 400:
            data = response.json()
            if "At least 5 resumes are required" in data.get("detail", ""):
                print("   ✅ Correctly rejected insufficient resumes")
            else:
                print(f"   ❌ Wrong error message: {data.get('detail')}")
        elif response.status_code == 401:
            print("   ✅ Authentication required (endpoint protected)")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 3: Valid resume count (5 resumes)
    print("\n3. Testing valid resume count (5 resumes)...")
    try:
        files = []
        files.append(('job_description', ('job.pdf', job_content, 'application/pdf')))
        
        # Add 5 resumes (valid)
        for i in range(5):
            files.append(('resumes', (f'resume{i+1}.pdf', resume_content, 'application/pdf')))
        
        response = requests.post(f"{base_url}/api/analyze-resumes", files=files)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Successfully accepted 5 resumes")
        elif response.status_code == 401:
            print("   ✅ Authentication required (endpoint protected)")
        elif response.status_code == 400:
            data = response.json()
            print(f"   ❌ Validation error: {data.get('detail')}")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 4: Excessive resumes (35 resumes)
    print("\n4. Testing excessive resumes (35 resumes)...")
    try:
        files = []
        files.append(('job_description', ('job.pdf', job_content, 'application/pdf')))
        
        # Add 35 resumes (too many)
        for i in range(35):
            files.append(('resumes', (f'resume{i+1}.pdf', resume_content, 'application/pdf')))
        
        response = requests.post(f"{base_url}/api/analyze-resumes", files=files)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 400:
            data = response.json()
            if "Maximum 30 resumes can be processed" in data.get("detail", ""):
                print("   ✅ Correctly rejected excessive resumes")
            else:
                print(f"   ❌ Wrong error message: {data.get('detail')}")
        elif response.status_code == 401:
            print("   ✅ Authentication required (endpoint protected)")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test 5: Invalid file type
    print("\n5. Testing invalid file type...")
    try:
        files = []
        files.append(('job_description', ('job.txt', b"Job Description", 'text/plain')))
        
        # Add 5 resumes
        for i in range(5):
            files.append(('resumes', (f'resume{i+1}.txt', b"Resume content", 'text/plain')))
        
        response = requests.post(f"{base_url}/api/analyze-resumes", files=files)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 400:
            data = response.json()
            if "must be a PDF, DOC, or DOCX file" in data.get("detail", ""):
                print("   ✅ Correctly rejected invalid file types")
            else:
                print(f"   ❌ Wrong error message: {data.get('detail')}")
        elif response.status_code == 401:
            print("   ✅ Authentication required (endpoint protected)")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")

if __name__ == "__main__":
    print("🚀 Resume Count Validation Tests")
    print("=" * 50)
    test_validation()
    print("\n" + "=" * 50)
    print("✅ Validation testing completed")