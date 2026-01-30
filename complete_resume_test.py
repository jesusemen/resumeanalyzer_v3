#!/usr/bin/env python3
"""
Complete Protected Resume Analysis Test
Tests all validation aspects of the protected resume analysis endpoint
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

def test_complete_protected_resume_analysis():
    """Test all aspects of the protected resume analysis endpoint"""
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    test_results = []
    
    # Test 1: Invalid job description file type
    print("🧪 Test 1: Invalid job description file type...")
    
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
            print("✅ Job description file type validation working")
            test_results.append(True)
        else:
            print(f"❌ Unexpected error message: {error_data}")
            test_results.append(False)
    else:
        print(f"❌ Expected 400, got {response.status_code}")
        test_results.append(False)
    
    # Test 2: Resume count validation (less than 30)
    print("\n🧪 Test 2: Resume count validation (less than 30)...")
    
    # Create a mock PDF content
    pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n253\n%%EOF'
    
    job_file = io.BytesIO(pdf_content)
    
    # Create only 2 resume files (less than 30)
    files = {
        'job_description': ('job.pdf', job_file, 'application/pdf'),
        'resumes': [
            ('resume1.pdf', io.BytesIO(pdf_content), 'application/pdf'),
            ('resume2.pdf', io.BytesIO(pdf_content), 'application/pdf')
        ]
    }
    
    response = requests.post(f"{BACKEND_URL}/analyze-resumes", files=files, headers=headers)
    
    if response.status_code == 400:
        error_data = response.json()
        if "30 resumes" in error_data.get("detail", ""):
            print("✅ Resume count validation working")
            test_results.append(True)
        else:
            print(f"❌ Unexpected error message: {error_data}")
            test_results.append(False)
    else:
        print(f"❌ Expected 400, got {response.status_code}: {response.text}")
        test_results.append(False)
    
    # Test 3: Invalid resume file type
    print("\n🧪 Test 3: Invalid resume file type...")
    
    job_file = io.BytesIO(pdf_content)
    
    # Create 30 resume files but with invalid type for one
    resume_files = []
    for i in range(29):
        resume_files.append(('resumes', (f'resume{i+1}.pdf', io.BytesIO(pdf_content), 'application/pdf')))
    
    # Add one invalid file type
    resume_files.append(('resumes', ('invalid_resume.txt', io.BytesIO(b'Invalid resume content'), 'text/plain')))
    
    files = [('job_description', ('job.pdf', job_file, 'application/pdf'))] + resume_files
    
    response = requests.post(f"{BACKEND_URL}/analyze-resumes", files=files, headers=headers)
    
    if response.status_code == 400:
        error_data = response.json()
        if "must be a PDF, DOC, or DOCX file" in error_data.get("detail", ""):
            print("✅ Resume file type validation working")
            test_results.append(True)
        else:
            print(f"❌ Unexpected error message: {error_data}")
            test_results.append(False)
    else:
        print(f"❌ Expected 400, got {response.status_code}: {response.text}")
        test_results.append(False)
    
    return all(test_results)

if __name__ == "__main__":
    print("🚀 Testing Complete Protected Resume Analysis Endpoint")
    print("=" * 60)
    
    success = test_complete_protected_resume_analysis()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All protected resume analysis validation tests passed!")
    else:
        print("⚠️ Some protected resume analysis validation tests failed")
    
    exit(0 if success else 1)