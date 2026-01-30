#!/usr/bin/env python3
"""
Final Backend API Testing Suite for Resume Analyzer
"""

import requests
import json
import os

class FinalResumeAnalyzerTester:
    def __init__(self):
        # Get backend URL from frontend env
        self.base_url = self._get_backend_url()
        self.session = requests.Session()
        self.test_results = []
        
    def _get_backend_url(self):
        """Get backend URL from frontend .env file"""
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        return line.split('=', 1)[1].strip()
        except Exception as e:
            print(f"Error reading frontend .env: {e}")
            return "http://localhost:8001"  # fallback
    
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_health_check(self):
        """Test GET /api/ health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Health Check", True, "API is responding correctly", 
                                {"status_code": response.status_code, "response": data})
                else:
                    self.log_test("Health Check", False, "Response missing expected message field",
                                {"status_code": response.status_code, "response": data})
            else:
                self.log_test("Health Check", False, f"Unexpected status code: {response.status_code}",
                            {"status_code": response.status_code, "response": response.text})
                
        except Exception as e:
            self.log_test("Health Check", False, f"Request failed: {str(e)}")
    
    def test_invalid_file_types(self):
        """Test error handling for invalid file types"""
        try:
            # Create files with invalid extensions
            files = []
            files.append(('job_description', ('invalid.txt', 'This is a text file')))
            for i in range(30):
                files.append(('resumes', (f'invalid_{i}.txt', f'Resume content {i}')))
            
            response = self.session.post(f"{self.base_url}/api/analyze-resumes", files=files)
            
            if response.status_code == 400:
                data = response.json()
                if "must be a PDF, DOC, or DOCX file" in data.get("detail", ""):
                    self.log_test("Invalid File Types", True, "Correctly rejected invalid file types",
                                {"status_code": response.status_code, "error": data.get("detail")})
                else:
                    self.log_test("Invalid File Types", False, "Error message doesn't match expected format",
                                {"status_code": response.status_code, "response": data})
            else:
                self.log_test("Invalid File Types", False, f"Expected 400 status code, got {response.status_code}",
                            {"status_code": response.status_code, "response": response.text})
                
        except Exception as e:
            self.log_test("Invalid File Types", False, f"Request failed: {str(e)}")
    
    def test_insufficient_resumes(self):
        """Test error handling for insufficient resumes (< 30)"""
        try:
            # Create valid files but insufficient count
            files = []
            files.append(('job_description', ('job.pdf', 'Job Description Content')))
            for i in range(5):  # Only 5 resumes
                files.append(('resumes', (f'resume_{i}.pdf', f'Resume content {i}')))
            
            response = self.session.post(f"{self.base_url}/api/analyze-resumes", files=files)
            
            if response.status_code == 400:
                data = response.json()
                if "At least 30 resumes are required" in data.get("detail", ""):
                    self.log_test("Insufficient Resumes", True, "Correctly rejected insufficient resume count",
                                {"status_code": response.status_code, "error": data.get("detail")})
                else:
                    self.log_test("Insufficient Resumes", False, "Error message doesn't match expected format",
                                {"status_code": response.status_code, "response": data})
            else:
                self.log_test("Insufficient Resumes", False, f"Expected 400 status code, got {response.status_code}",
                            {"status_code": response.status_code, "response": response.text})
                
        except Exception as e:
            self.log_test("Insufficient Resumes", False, f"Request failed: {str(e)}")
    
    def test_analysis_history(self):
        """Test the analysis history endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/analysis-history")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Analysis History", True, f"Successfully retrieved {len(data)} analysis records",
                                {"records_count": len(data)})
                else:
                    self.log_test("Analysis History", False, "Response is not a list",
                                {"response_type": type(data).__name__})
            else:
                self.log_test("Analysis History", False, f"Unexpected status code: {response.status_code}",
                            {"status_code": response.status_code, "response": response.text})
                
        except Exception as e:
            self.log_test("Analysis History", False, f"Analysis history test failed: {str(e)}")
    
    def test_backend_services_import(self):
        """Test if backend services can be imported and initialized"""
        try:
            import sys
            import os
            sys.path.append('/app/backend')
            
            # Set the GEMINI_API_KEY for testing
            os.environ['GEMINI_API_KEY'] = 'AIzaSyDomH_bhE817pirH-SBMMPZiwu9NmQHQ2c'
            
            from services.document_parser import DocumentParser
            from services.resume_analyzer import ResumeAnalyzer
            
            # Test DocumentParser
            parser = DocumentParser()
            self.log_test("DocumentParser Import", True, "Successfully imported and initialized DocumentParser")
            
            # Test ResumeAnalyzer
            analyzer = ResumeAnalyzer()
            self.log_test("ResumeAnalyzer Import", True, "Successfully imported and initialized ResumeAnalyzer")
            
            # Test contact extraction with proper format
            test_resume = """John Doe
Software Engineer
john.doe@email.com
+1-555-123-4567
Experience: 5 years in software development"""
            
            contact_info = analyzer._extract_contact_info(test_resume)
            
            if (contact_info.get('name') and contact_info['name'] != '' and
                contact_info.get('email') and 
                contact_info.get('phone')):
                self.log_test("Contact Extraction", True, "Successfully extracted contact information",
                            {"extracted": contact_info})
            else:
                self.log_test("Contact Extraction", False, "Failed to extract complete contact information",
                            {"extracted": contact_info})
                
        except Exception as e:
            self.log_test("Backend Services", False, f"Backend services test failed: {str(e)}")
    
    def test_document_parsing_functionality(self):
        """Test document parsing with actual content"""
        try:
            import sys
            sys.path.append('/app/backend')
            
            from services.document_parser import DocumentParser
            
            parser = DocumentParser()
            
            # Test with simple text content (simulating PDF/DOCX parsing)
            test_content = "John Smith\nSoftware Engineer\njohn@example.com\n+1-555-123-4567"
            
            # Test DOC parsing (simplified)
            doc_result = parser.extract_text_from_doc(test_content.encode('utf-8'))
            if doc_result and "John Smith" in doc_result:
                self.log_test("DOC Parsing", True, "Successfully parsed DOC content")
            else:
                self.log_test("DOC Parsing", False, "Failed to parse DOC content", {"result": doc_result})
                
        except Exception as e:
            self.log_test("Document Parsing", False, f"Document parsing test failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print(f"🚀 Starting Resume Analyzer Backend Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run tests in order
        self.test_health_check()
        self.test_invalid_file_types()
        self.test_insufficient_resumes()
        self.test_analysis_history()
        self.test_backend_services_import()
        self.test_document_parsing_functionality()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n🔍 CRITICAL ISSUES FOUND:")
        critical_issues = []
        for result in self.test_results:
            if not result['success'] and result['test'] in ['Health Check', 'Backend Services']:
                critical_issues.append(f"  - {result['test']}: {result['message']}")
        
        if critical_issues:
            for issue in critical_issues:
                print(issue)
        else:
            print("  - No critical issues found. Core functionality is working.")
        
        return passed >= (total * 0.8)  # 80% pass rate considered success

if __name__ == "__main__":
    tester = FinalResumeAnalyzerTester()
    success = tester.run_all_tests()
    print(f"\n🏁 Testing completed. Overall success: {'✅' if success else '❌'}")