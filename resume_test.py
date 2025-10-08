#!/usr/bin/env python3
"""
Quick test for resume upload endpoint
"""

import requests

BASE_URL = "https://jobtrack-ai-1.preview.emergentagent.com/api"

# First create a test student
student_data = {
    "name": "Test Student",
    "email": "test@example.com",
    "phone": "+1-555-0000"
}

response = requests.post(f"{BASE_URL}/students", json=student_data)
if response.status_code == 200:
    student = response.json()
    student_id = student["id"]
    print(f"✅ Created test student: {student_id}")
    
    # Test resume upload with form data
    resume_text = "This is a test resume content"
    form_data = {"resume_text": resume_text}
    
    response = requests.post(f"{BASE_URL}/students/{student_id}/resume", data=form_data)
    print(f"Resume upload status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Resume upload successful")
        print(response.json())
    else:
        print("❌ Resume upload failed")
        print(response.text)
    
    # Cleanup
    requests.delete(f"{BASE_URL}/students/{student_id}")
    print("✅ Cleaned up test student")
else:
    print("❌ Failed to create test student")