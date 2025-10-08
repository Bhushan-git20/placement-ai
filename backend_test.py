#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Placement Management System
Tests all FastAPI endpoints including CRUD operations and AI features
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://jobtrack-ai-1.preview.emergentagent.com/api"
TIMEOUT = 30

class PlacementBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        
        # Test data storage
        self.test_student_id = None
        self.test_job_id = None
        self.test_application_id = None
        self.test_test_id = None
        
        # Results tracking
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name, success, message="", response_data=None):
        """Log test results"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.results["failed"] += 1
            error_msg = f"❌ {test_name}: {message}"
            if response_data:
                error_msg += f" | Response: {response_data}"
            print(error_msg)
            self.results["errors"].append(error_msg)
    
    def make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            return None, str(e)
    
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        print("\n=== Testing Root Endpoint ===")
        response = self.make_request("GET", "/")
        
        if response and response.status_code == 200:
            data = response.json()
            if "message" in data and "endpoints" in data:
                self.log_result("Root Endpoint", True, "API info retrieved successfully")
                return True
            else:
                self.log_result("Root Endpoint", False, "Invalid response structure", data)
        else:
            error_msg = f"Status: {response.status_code if response else 'No response'}"
            self.log_result("Root Endpoint", False, error_msg)
        return False
    
    def test_students_crud(self):
        """Test all student CRUD operations"""
        print("\n=== Testing Students CRUD Operations ===")
        
        # Test data
        student_data = {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@university.edu",
            "phone": "+1-555-0123",
            "education": [
                {
                    "degree": "Bachelor of Computer Science",
                    "university": "Tech University",
                    "year": 2024,
                    "gpa": 3.8
                }
            ],
            "skills": [
                {"name": "Python", "proficiency": "advanced"},
                {"name": "JavaScript", "proficiency": "intermediate"},
                {"name": "React", "proficiency": "intermediate"}
            ],
            "experience": [
                {
                    "company": "TechCorp Internship",
                    "role": "Software Development Intern",
                    "duration": "3 months",
                    "description": "Developed web applications using React and Node.js"
                }
            ]
        }
        
        # 1. Create Student
        response = self.make_request("POST", "/students", student_data)
        if response and response.status_code == 200:
            student = response.json()
            self.test_student_id = student.get("id")
            self.log_result("Create Student", True, f"Student created with ID: {self.test_student_id}")
        else:
            self.log_result("Create Student", False, f"Status: {response.status_code if response else 'No response'}")
            return False
        
        # 2. Get Student by ID
        if self.test_student_id:
            response = self.make_request("GET", f"/students/{self.test_student_id}")
            if response and response.status_code == 200:
                student = response.json()
                if student.get("name") == student_data["name"]:
                    self.log_result("Get Student by ID", True, "Student retrieved successfully")
                else:
                    self.log_result("Get Student by ID", False, "Student data mismatch")
            else:
                self.log_result("Get Student by ID", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 3. Get All Students
        response = self.make_request("GET", "/students")
        if response and response.status_code == 200:
            students = response.json()
            if isinstance(students, list) and len(students) > 0:
                self.log_result("Get All Students", True, f"Retrieved {len(students)} students")
            else:
                self.log_result("Get All Students", False, "No students found or invalid response")
        else:
            self.log_result("Get All Students", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 4. Update Student
        if self.test_student_id:
            update_data = {
                "name": "Sarah Johnson Updated",
                "phone": "+1-555-9999"
            }
            response = self.make_request("PUT", f"/students/{self.test_student_id}", update_data)
            if response and response.status_code == 200:
                updated_student = response.json()
                if updated_student.get("name") == update_data["name"]:
                    self.log_result("Update Student", True, "Student updated successfully")
                else:
                    self.log_result("Update Student", False, "Update not reflected")
            else:
                self.log_result("Update Student", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 5. Upload Resume
        if self.test_student_id:
            resume_text = "Experienced software developer with expertise in Python, JavaScript, and React. Strong background in web development and database management."
            response = self.make_request("POST", f"/students/{self.test_student_id}/resume", {"resume_text": resume_text})
            if response and response.status_code == 200:
                self.log_result("Upload Resume", True, "Resume uploaded successfully")
            else:
                self.log_result("Upload Resume", False, f"Status: {response.status_code if response else 'No response'}")
        
        return True
    
    def test_jobs_crud(self):
        """Test all job CRUD operations"""
        print("\n=== Testing Jobs CRUD Operations ===")
        
        # Test data
        job_data = {
            "title": "Senior Software Engineer",
            "company": "InnovateTech Solutions",
            "description": "We are seeking a talented Senior Software Engineer to join our dynamic team. You will be responsible for designing, developing, and maintaining high-quality software applications.",
            "requirements": [
                "5+ years of software development experience",
                "Proficiency in Python, JavaScript, and React",
                "Experience with cloud platforms (AWS, Azure)",
                "Strong problem-solving skills",
                "Bachelor's degree in Computer Science or related field"
            ],
            "location": "San Francisco, CA",
            "salary_range": "$120,000 - $160,000",
            "job_type": "full-time"
        }
        
        # 1. Create Job
        response = self.make_request("POST", "/jobs", job_data)
        if response and response.status_code == 200:
            job = response.json()
            self.test_job_id = job.get("id")
            self.log_result("Create Job", True, f"Job created with ID: {self.test_job_id}")
        else:
            self.log_result("Create Job", False, f"Status: {response.status_code if response else 'No response'}")
            return False
        
        # 2. Get Job by ID
        if self.test_job_id:
            response = self.make_request("GET", f"/jobs/{self.test_job_id}")
            if response and response.status_code == 200:
                job = response.json()
                if job.get("title") == job_data["title"]:
                    self.log_result("Get Job by ID", True, "Job retrieved successfully")
                else:
                    self.log_result("Get Job by ID", False, "Job data mismatch")
            else:
                self.log_result("Get Job by ID", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 3. Get All Jobs
        response = self.make_request("GET", "/jobs")
        if response and response.status_code == 200:
            jobs = response.json()
            if isinstance(jobs, list) and len(jobs) > 0:
                self.log_result("Get All Jobs", True, f"Retrieved {len(jobs)} jobs")
            else:
                self.log_result("Get All Jobs", False, "No jobs found or invalid response")
        else:
            self.log_result("Get All Jobs", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 4. Update Job
        if self.test_job_id:
            update_data = {
                "title": "Senior Software Engineer - Updated",
                "company": "InnovateTech Solutions",
                "description": job_data["description"],
                "requirements": job_data["requirements"],
                "location": "Remote",
                "salary_range": "$130,000 - $170,000",
                "job_type": "full-time"
            }
            response = self.make_request("PUT", f"/jobs/{self.test_job_id}", update_data)
            if response and response.status_code == 200:
                updated_job = response.json()
                if updated_job.get("location") == "Remote":
                    self.log_result("Update Job", True, "Job updated successfully")
                else:
                    self.log_result("Update Job", False, "Update not reflected")
            else:
                self.log_result("Update Job", False, f"Status: {response.status_code if response else 'No response'}")
        
        return True
    
    def test_applications_crud(self):
        """Test application system"""
        print("\n=== Testing Applications CRUD Operations ===")
        
        if not self.test_student_id or not self.test_job_id:
            self.log_result("Applications Test", False, "Missing student or job ID for testing")
            return False
        
        # 1. Submit Application
        application_data = {
            "student_id": self.test_student_id,
            "job_id": self.test_job_id,
            "notes": "I am very interested in this position and believe my skills align well with the requirements."
        }
        
        response = self.make_request("POST", "/applications", application_data)
        if response and response.status_code == 200:
            application = response.json()
            self.test_application_id = application.get("id")
            self.log_result("Submit Application", True, f"Application submitted with ID: {self.test_application_id}")
        else:
            self.log_result("Submit Application", False, f"Status: {response.status_code if response else 'No response'}")
            return False
        
        # 2. Get Student Applications
        response = self.make_request("GET", f"/applications/student/{self.test_student_id}")
        if response and response.status_code == 200:
            applications = response.json()
            if isinstance(applications, list) and len(applications) > 0:
                self.log_result("Get Student Applications", True, f"Retrieved {len(applications)} applications")
            else:
                self.log_result("Get Student Applications", False, "No applications found")
        else:
            self.log_result("Get Student Applications", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 3. Get All Applications
        response = self.make_request("GET", "/applications")
        if response and response.status_code == 200:
            applications = response.json()
            if isinstance(applications, list):
                self.log_result("Get All Applications", True, f"Retrieved {len(applications)} applications")
            else:
                self.log_result("Get All Applications", False, "Invalid response format")
        else:
            self.log_result("Get All Applications", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 4. Update Application Status
        if self.test_application_id:
            response = self.make_request("PUT", f"/applications/{self.test_application_id}/status", params={"status": "under_review"})
            if response and response.status_code == 200:
                self.log_result("Update Application Status", True, "Status updated to under_review")
            else:
                self.log_result("Update Application Status", False, f"Status: {response.status_code if response else 'No response'}")
        
        return True
    
    def test_tests_system(self):
        """Test the testing system"""
        print("\n=== Testing Tests System ===")
        
        # 1. Create Test
        test_data = {
            "title": "Python Programming Assessment",
            "description": "Basic Python programming knowledge test",
            "category": "Programming",
            "duration_minutes": 30,
            "questions": [
                {
                    "question": "What is the output of print(2 ** 3)?",
                    "options": ["6", "8", "9", "16"],
                    "correct_answer": 1
                },
                {
                    "question": "Which of the following is a mutable data type in Python?",
                    "options": ["tuple", "string", "list", "int"],
                    "correct_answer": 2
                },
                {
                    "question": "What does the len() function return?",
                    "options": ["The length of an object", "The type of an object", "The value of an object", "None"],
                    "correct_answer": 0
                }
            ]
        }
        
        response = self.make_request("POST", "/tests", test_data)
        if response and response.status_code == 200:
            test = response.json()
            self.test_test_id = test.get("id")
            self.log_result("Create Test", True, f"Test created with ID: {self.test_test_id}")
        else:
            self.log_result("Create Test", False, f"Status: {response.status_code if response else 'No response'}")
            return False
        
        # 2. Get All Tests
        response = self.make_request("GET", "/tests")
        if response and response.status_code == 200:
            tests = response.json()
            if isinstance(tests, list) and len(tests) > 0:
                self.log_result("Get All Tests", True, f"Retrieved {len(tests)} tests")
            else:
                self.log_result("Get All Tests", False, "No tests found")
        else:
            self.log_result("Get All Tests", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 3. Get Test by ID
        if self.test_test_id:
            response = self.make_request("GET", f"/tests/{self.test_test_id}")
            if response and response.status_code == 200:
                test = response.json()
                if test.get("title") == test_data["title"]:
                    self.log_result("Get Test by ID", True, "Test retrieved successfully")
                else:
                    self.log_result("Get Test by ID", False, "Test data mismatch")
            else:
                self.log_result("Get Test by ID", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 4. Submit Test Answers
        if self.test_test_id and self.test_student_id:
            submission_data = {
                "student_id": self.test_student_id,
                "test_id": self.test_test_id,
                "answers": [
                    {"question_index": 0, "selected_answer": 1},  # Correct
                    {"question_index": 1, "selected_answer": 2},  # Correct
                    {"question_index": 2, "selected_answer": 1}   # Incorrect
                ]
            }
            
            response = self.make_request("POST", "/tests/submit", submission_data)
            if response and response.status_code == 200:
                result = response.json()
                score = result.get("score", 0)
                self.log_result("Submit Test", True, f"Test submitted, score: {score}%")
            else:
                self.log_result("Submit Test", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 5. Get Student Test Results
        if self.test_student_id:
            response = self.make_request("GET", f"/test-results/student/{self.test_student_id}")
            if response and response.status_code == 200:
                results = response.json()
                if isinstance(results, list):
                    self.log_result("Get Student Test Results", True, f"Retrieved {len(results)} test results")
                else:
                    self.log_result("Get Student Test Results", False, "Invalid response format")
            else:
                self.log_result("Get Student Test Results", False, f"Status: {response.status_code if response else 'No response'}")
        
        return True
    
    def test_interview_questions(self):
        """Test interview questions endpoints"""
        print("\n=== Testing Interview Questions ===")
        
        # 1. Seed Interview Questions
        response = self.make_request("POST", "/interview-questions/seed")
        if response and response.status_code == 200:
            result = response.json()
            self.log_result("Seed Interview Questions", True, result.get("message", "Seeded successfully"))
        else:
            self.log_result("Seed Interview Questions", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 2. Get All Interview Questions
        response = self.make_request("GET", "/interview-questions")
        if response and response.status_code == 200:
            questions = response.json()
            if isinstance(questions, list) and len(questions) > 0:
                self.log_result("Get Interview Questions", True, f"Retrieved {len(questions)} questions")
            else:
                self.log_result("Get Interview Questions", False, "No questions found")
        else:
            self.log_result("Get Interview Questions", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 3. Get Filtered Interview Questions
        response = self.make_request("GET", "/interview-questions", params={"category": "Programming", "difficulty": "medium"})
        if response and response.status_code == 200:
            questions = response.json()
            if isinstance(questions, list):
                self.log_result("Get Filtered Interview Questions", True, f"Retrieved {len(questions)} filtered questions")
            else:
                self.log_result("Get Filtered Interview Questions", False, "Invalid response format")
        else:
            self.log_result("Get Filtered Interview Questions", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 4. Create Custom Interview Question
        question_data = {
            "question": "Explain the difference between synchronous and asynchronous programming.",
            "category": "Programming",
            "difficulty": "medium",
            "skills": ["Programming Concepts", "Async Programming"]
        }
        
        response = self.make_request("POST", "/interview-questions", question_data)
        if response and response.status_code == 200:
            question = response.json()
            self.log_result("Create Interview Question", True, f"Question created with ID: {question.get('id')}")
        else:
            self.log_result("Create Interview Question", False, f"Status: {response.status_code if response else 'No response'}")
        
        return True
    
    def test_ai_features(self):
        """Test AI-powered features (Critical - uses Emergent LLM)"""
        print("\n=== Testing AI Features (Emergent LLM) ===")
        
        if not self.test_student_id:
            self.log_result("AI Features Test", False, "Missing student ID for AI testing")
            return False
        
        # 1. Generate Job Matches
        print("Generating AI job matches (this may take a moment)...")
        response = self.make_request("POST", f"/ai/job-match/{self.test_student_id}")
        if response and response.status_code == 200:
            result = response.json()
            matches_count = len(result.get("matches", []))
            self.log_result("Generate Job Matches", True, f"Generated {matches_count} job matches")
        else:
            error_msg = f"Status: {response.status_code if response else 'No response'}"
            if response and response.status_code >= 400:
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                    error_msg += f" - {error_detail}"
                except:
                    pass
            self.log_result("Generate Job Matches", False, error_msg)
        
        # 2. Get Job Matches
        response = self.make_request("GET", f"/ai/job-match/{self.test_student_id}")
        if response and response.status_code == 200:
            matches = response.json()
            if isinstance(matches, list):
                self.log_result("Get Job Matches", True, f"Retrieved {len(matches)} job matches")
            else:
                self.log_result("Get Job Matches", False, "Invalid response format")
        else:
            self.log_result("Get Job Matches", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 3. Analyze Skill Gap
        print("Analyzing skill gaps with AI (this may take a moment)...")
        response = self.make_request("POST", f"/ai/skill-gap/{self.test_student_id}")
        if response and response.status_code == 200:
            skill_gap = response.json()
            missing_skills = len(skill_gap.get("missing_skills", []))
            self.log_result("Analyze Skill Gap", True, f"Identified {missing_skills} missing skills")
        else:
            error_msg = f"Status: {response.status_code if response else 'No response'}"
            if response and response.status_code >= 400:
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                    error_msg += f" - {error_detail}"
                except:
                    pass
            self.log_result("Analyze Skill Gap", False, error_msg)
        
        # 4. Get Skill Gap Analysis
        response = self.make_request("GET", f"/ai/skill-gap/{self.test_student_id}")
        if response and response.status_code == 200:
            skill_gap = response.json()
            if "missing_skills" in skill_gap and "ai_analysis" in skill_gap:
                self.log_result("Get Skill Gap Analysis", True, "Skill gap analysis retrieved")
            else:
                self.log_result("Get Skill Gap Analysis", False, "Invalid skill gap data structure")
        else:
            self.log_result("Get Skill Gap Analysis", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 5. Get Job Recommendations
        response = self.make_request("POST", f"/ai/job-recommendations/{self.test_student_id}")
        if response and response.status_code == 200:
            recommendations = response.json()
            rec_count = len(recommendations.get("recommendations", []))
            self.log_result("Get Job Recommendations", True, f"Retrieved {rec_count} job recommendations")
        else:
            self.log_result("Get Job Recommendations", False, f"Status: {response.status_code if response else 'No response'}")
        
        return True
    
    def test_analytics(self):
        """Test analytics endpoints"""
        print("\n=== Testing Analytics ===")
        
        # 1. Get Student Analytics
        if self.test_student_id:
            response = self.make_request("GET", f"/analytics/student/{self.test_student_id}")
            if response and response.status_code == 200:
                analytics = response.json()
                required_fields = ["total_applications", "application_status_breakdown", "total_tests_taken"]
                if all(field in analytics for field in required_fields):
                    self.log_result("Get Student Analytics", True, "Student analytics retrieved successfully")
                else:
                    self.log_result("Get Student Analytics", False, "Missing required analytics fields")
            else:
                self.log_result("Get Student Analytics", False, f"Status: {response.status_code if response else 'No response'}")
        
        # 2. Get Platform Overview
        response = self.make_request("GET", "/analytics/overview")
        if response and response.status_code == 200:
            overview = response.json()
            required_fields = ["total_students", "total_active_jobs", "total_applications"]
            if all(field in overview for field in required_fields):
                self.log_result("Get Platform Overview", True, "Platform overview retrieved successfully")
            else:
                self.log_result("Get Platform Overview", False, "Missing required overview fields")
        else:
            self.log_result("Get Platform Overview", False, f"Status: {response.status_code if response else 'No response'}")
        
        return True
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n=== Cleaning Up Test Data ===")
        
        # Delete test student (this will cascade to related data)
        if self.test_student_id:
            response = self.make_request("DELETE", f"/students/{self.test_student_id}")
            if response and response.status_code == 200:
                self.log_result("Delete Test Student", True, "Test student deleted")
            else:
                self.log_result("Delete Test Student", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Delete test job
        if self.test_job_id:
            response = self.make_request("DELETE", f"/jobs/{self.test_job_id}")
            if response and response.status_code == 200:
                self.log_result("Delete Test Job", True, "Test job deleted")
            else:
                self.log_result("Delete Test Job", False, f"Status: {response.status_code if response else 'No response'}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Placement Management System Backend Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Students CRUD", self.test_students_crud),
            ("Jobs CRUD", self.test_jobs_crud),
            ("Applications CRUD", self.test_applications_crud),
            ("Tests System", self.test_tests_system),
            ("Interview Questions", self.test_interview_questions),
            ("AI Features", self.test_ai_features),
            ("Analytics", self.test_analytics),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_result(f"{test_name} (Exception)", False, str(e))
        
        # Cleanup
        self.cleanup_test_data()
        
        # Final results
        print("\n" + "=" * 60)
        print("🏁 FINAL TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['failed'] > 0:
            print(f"\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100 if self.results['total_tests'] > 0 else 0
        print(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Backend testing completed successfully!")
        elif success_rate >= 60:
            print("⚠️  Backend has some issues but core functionality works")
        else:
            print("🚨 Backend has significant issues that need attention")
        
        return self.results

if __name__ == "__main__":
    tester = PlacementBackendTester()
    results = tester.run_all_tests()