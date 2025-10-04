from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from enum import Enum
import json


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
from emergentintegrations.llm.chat import LlmChat, UserMessage
import base64
import io
app = FastAPI(title="Placement AI API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("SECRET_KEY", "placement-ai-secret-key-change-in-production")
ALGORITHM = "HS256"

# Enums for User Roles
class UserRole(str, Enum):
    STUDENT = "student"
    RECRUITER = "recruiter"
    FACULTY = "faculty"
    ADMIN = "admin"

class JobStatus(str, Enum):
# AI Integration
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "sk-emergent-b4aC635415a2959C20")
    ACTIVE = "active"
    CLOSED = "closed"
    DRAFT = "draft"

class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    REJECTED = "rejected"
    SELECTED = "selected"

class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Pydantic Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class StudentProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    university: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[int] = None
    skills: List[str] = []
    resume_url: Optional[str] = None
    gpa: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CompanyProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recruiter_id: str
    company_name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Job(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recruiter_id: str
    company_id: str
    title: str
    description: str
    requirements: List[str] = []
    location: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None  # full-time, part-time, internship
    status: JobStatus = JobStatus.ACTIVE
    application_deadline: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Application(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    student_id: str
    cover_letter: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.SUBMITTED
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Interview(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    application_id: str
    recruiter_id: str
    student_id: str
    scheduled_at: datetime
    interview_type: str  # online, offline, phone
    location_or_link: Optional[str] = None
    status: InterviewStatus = InterviewStatus.SCHEDULED
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SkillAssessment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    faculty_id: str
    title: str
    description: str
    questions: List[Dict[str, Any]] = []  # Flexible structure for different question types
    duration_minutes: int
    passing_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AssessmentResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    assessment_id: str
    student_id: str
    answers: List[Dict[str, Any]] = []
    score: Optional[float] = None
    passed: bool = False
    completed_at: datetime = Field(default_factory=datetime.utcnow)

# Create models with db operations
class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(**user)

def require_role(allowed_roles: List[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
# Student Profile endpoints
@api_router.get("/students/profile", response_model=StudentProfile)
async def get_student_profile(current_user: User = Depends(require_role([UserRole.STUDENT]))):
    profile = await db.student_profiles.find_one({"user_id": current_user.id})
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        await db.student_profiles.insert_one(profile.dict())
    return StudentProfile(**profile)

@api_router.put("/students/profile", response_model=StudentProfile)
async def update_student_profile(
    profile_data: dict,
    current_user: User = Depends(require_role([UserRole.STUDENT, UserRole.FACULTY, UserRole.ADMIN]))
):
    user_id = current_user.id
    # Faculty and Admin can update any student profile via user_id in request
    if current_user.role in [UserRole.FACULTY, UserRole.ADMIN] and "user_id" in profile_data:
        user_id = profile_data["user_id"]
    
    profile_data["updated_at"] = datetime.utcnow()
    await db.student_profiles.update_one(
        {"user_id": user_id},
        {"$set": profile_data}
    )
    
    updated_profile = await db.student_profiles.find_one({"user_id": user_id})
    return StudentProfile(**updated_profile)

# Company Profile endpoints
@api_router.post("/companies", response_model=CompanyProfile)
async def create_company_profile(
    company_data: dict,
    current_user: User = Depends(require_role([UserRole.RECRUITER, UserRole.ADMIN]))
):
    company = CompanyProfile(**company_data, recruiter_id=current_user.id)
    await db.company_profiles.insert_one(company.dict())
    return company

@api_router.get("/companies/my", response_model=List[CompanyProfile])
async def get_my_companies(current_user: User = Depends(require_role([UserRole.RECRUITER, UserRole.ADMIN]))):
    companies = await db.company_profiles.find({"recruiter_id": current_user.id}).to_list(100)
    return [CompanyProfile(**company) for company in companies]

@api_router.get("/companies", response_model=List[CompanyProfile])
async def get_all_companies():
    companies = await db.company_profiles.find().to_list(100)
    return [CompanyProfile(**company) for company in companies]

# Job endpoints
@api_router.post("/jobs", response_model=Job)
async def create_job(
    job_data: dict,
    current_user: User = Depends(require_role([UserRole.RECRUITER, UserRole.ADMIN]))
):
    job = Job(**job_data, recruiter_id=current_user.id)
    await db.jobs.insert_one(job.dict())
    return job

@api_router.get("/jobs", response_model=List[Job])
async def get_jobs(
    status: Optional[JobStatus] = None,
    company_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    query = {}
    if status:
        query["status"] = status
    if company_id:
        query["company_id"] = company_id
    
    jobs = await db.jobs.find(query).skip(skip).limit(limit).to_list(limit)
    return [Job(**job) for job in jobs]

@api_router.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    job = await db.jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return Job(**job)

@api_router.put("/jobs/{job_id}", response_model=Job)
async def update_job(
    job_id: str,
    job_data: dict,
    current_user: User = Depends(require_role([UserRole.RECRUITER, UserRole.ADMIN]))
):
    job = await db.jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check ownership
    if current_user.role != UserRole.ADMIN and job["recruiter_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this job")
    
    job_data["updated_at"] = datetime.utcnow()
    await db.jobs.update_one({"id": job_id}, {"$set": job_data})
    
    updated_job = await db.jobs.find_one({"id": job_id})
    return Job(**updated_job)

# Application endpoints
@api_router.post("/applications", response_model=Application)
async def apply_for_job(
    application_data: dict,
    current_user: User = Depends(require_role([UserRole.STUDENT]))
):
    # Check if job exists and is active
    job = await db.jobs.find_one({"id": application_data["job_id"]})
    if not job or job["status"] != JobStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Job not available")
    
    # Check if already applied
    existing_application = await db.applications.find_one({
        "job_id": application_data["job_id"],
        "student_id": current_user.id
    })
    if existing_application:
        raise HTTPException(status_code=400, detail="Already applied for this job")
    
    application = Application(**application_data, student_id=current_user.id)
    await db.applications.insert_one(application.dict())
    return application

@api_router.get("/applications/my", response_model=List[Application])
async def get_my_applications(current_user: User = Depends(require_role([UserRole.STUDENT]))):
    applications = await db.applications.find({"student_id": current_user.id}).to_list(100)
    return [Application(**app) for app in applications]

@api_router.get("/applications/job/{job_id}", response_model=List[Application])
async def get_job_applications(
    job_id: str,
    current_user: User = Depends(require_role([UserRole.RECRUITER, UserRole.ADMIN]))
):
    # Verify job ownership
    job = await db.jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if current_user.role != UserRole.ADMIN and job["recruiter_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view applications")
    
    applications = await db.applications.find({"job_id": job_id}).to_list(100)
    return [Application(**app) for app in applications]

@api_router.put("/applications/{application_id}/status", response_model=Application)
async def update_application_status(
    application_id: str,
    status_data: dict,
    current_user: User = Depends(require_role([UserRole.RECRUITER, UserRole.ADMIN]))
):
    application = await db.applications.find_one({"id": application_id})
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Verify job ownership
    job = await db.jobs.find_one({"id": application["job_id"]})
    if current_user.role != UserRole.ADMIN and job["recruiter_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this application")
    
    status_data["updated_at"] = datetime.utcnow()
    await db.applications.update_one({"id": application_id}, {"$set": status_data})
    
    updated_application = await db.applications.find_one({"id": application_id})
    return Application(**updated_application)

# Interview endpoints
@api_router.post("/interviews", response_model=Interview)
async def schedule_interview(
    interview_data: dict,
    current_user: User = Depends(require_role([UserRole.RECRUITER, UserRole.ADMIN]))
):
    # Verify application and job ownership
    application = await db.applications.find_one({"id": interview_data["application_id"]})
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    job = await db.jobs.find_one({"id": application["job_id"]})
    if current_user.role != UserRole.ADMIN and job["recruiter_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to schedule interview")
    
    interview = Interview(
        **interview_data,
        recruiter_id=current_user.id,
        student_id=application["student_id"]
    )
    await db.interviews.insert_one(interview.dict())
    
    # Update application status
    await db.applications.update_one(
        {"id": interview_data["application_id"]},
        {"$set": {"status": ApplicationStatus.INTERVIEW_SCHEDULED}}
    )
    
    return interview

@api_router.get("/interviews/my", response_model=List[Interview])
async def get_my_interviews(current_user: User = Depends(get_current_user)):
    query = {}
    if current_user.role == UserRole.STUDENT:
        query["student_id"] = current_user.id
    elif current_user.role == UserRole.RECRUITER:
        query["recruiter_id"] = current_user.id
    
    interviews = await db.interviews.find(query).to_list(100)
    return [Interview(**interview) for interview in interviews]

# Skill Assessment endpoints (Faculty and Admin only)
@api_router.post("/assessments", response_model=SkillAssessment)
async def create_skill_assessment(
    assessment_data: dict,
    current_user: User = Depends(require_role([UserRole.FACULTY, UserRole.ADMIN]))
):
    assessment = SkillAssessment(**assessment_data, faculty_id=current_user.id)
    await db.skill_assessments.insert_one(assessment.dict())
    return assessment

@api_router.get("/assessments", response_model=List[SkillAssessment])
async def get_skill_assessments(current_user: User = Depends(get_current_user)):
    assessments = await db.skill_assessments.find().to_list(100)
    return [SkillAssessment(**assessment) for assessment in assessments]

@api_router.post("/assessments/{assessment_id}/submit", response_model=AssessmentResult)
async def submit_assessment(
    assessment_id: str,
    result_data: dict,
    current_user: User = Depends(require_role([UserRole.STUDENT]))
):
    assessment = await db.skill_assessments.find_one({"id": assessment_id})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Calculate score (simple implementation)
    total_questions = len(assessment["questions"])
    correct_answers = 0
    
    for i, answer in enumerate(result_data.get("answers", [])):
        if i < total_questions:
            correct_answer = assessment["questions"][i].get("correct_answer")
            if answer.get("answer") == correct_answer:
                correct_answers += 1
    
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    passed = score >= assessment["passing_score"]
    
# AI Integration endpoints
@api_router.post("/ai/parse-resume")
async def parse_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role([UserRole.STUDENT, UserRole.FACULTY, UserRole.ADMIN]))
):
    try:
        # Read file content
        file_content = await file.read()
        
        # Convert to text for parsing (simplified - in production, use proper document parsing)
        if file.content_type == "application/pdf":
            # For PDF files, we'll extract text (simplified approach)
            text_content = f"Resume file uploaded: {file.filename}"
        else:
            text_content = file_content.decode('utf-8') if isinstance(file_content, bytes) else str(file_content)
        
        # Use AI to parse resume
        prompt = f"""
        Parse the following resume and extract structured information in JSON format:
        
        Resume Content:
        {text_content}
        
        Please extract and return a JSON object with the following fields:
        - full_name: string
        - email: string
        - phone: string
        - skills: array of strings
        - education: array of objects with (degree, institution, year)
        - experience: array of objects with (title, company, duration, description)
        - summary: string (brief professional summary)
        
        Return only the JSON object, no additional text.
        """
        
        # Initialize LLM chat for resume parsing
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"resume_parse_{current_user.id}",
            system_message="You are a resume parsing expert. Extract structured information from resumes and return valid JSON."
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse AI response
        ai_response = response
        
        try:
            parsed_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback if AI doesn't return valid JSON
            parsed_data = {
                "full_name": current_user.full_name,
                "email": current_user.email,
                "skills": [],
                "education": [],
                "experience": [],
                "summary": "AI parsing failed - manual review needed"
            }
        
        return {
            "status": "success",
            "parsed_data": parsed_data,
            "ai_response": ai_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

@api_router.post("/ai/career-chat")
async def career_chat(
    chat_data: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        user_message = chat_data.get("message", "")
        conversation_history = chat_data.get("history", [])
        
        # Get user profile for context
        context = f"User: {current_user.full_name}, Role: {current_user.role}"
        
        if current_user.role == UserRole.STUDENT:
            profile = await db.student_profiles.find_one({"user_id": current_user.id})
            if profile:
                context += f", Skills: {', '.join(profile.get('skills', []))}, Degree: {profile.get('degree', 'N/A')}"
        
        # Initialize LLM chat for career counseling
        system_message = f"""You are a helpful career counselor and placement advisor. 
        You help students with career guidance, job search strategies, interview preparation, 
        and skill development. Always provide practical, actionable advice.
        
        User Context: {context}
        
        Focus on:
        - Career path recommendations
        - Skill development suggestions  
        - Job search strategies
        - Interview preparation
        - Resume improvement tips
        - Industry insights
        """
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"career_chat_{current_user.id}",
            system_message=system_message
        ).with_model("openai", "gpt-4o-mini")
        
        # Build conversation with history
        full_message = user_message
        if conversation_history:
            # Add recent conversation context
            recent_history = conversation_history[-5:]  # Keep last 5 messages for context
            history_text = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in recent_history])
            full_message = f"Previous conversation:\n{history_text}\n\nNew question: {user_message}"
        
        user_msg = UserMessage(text=full_message)
        ai_response = await chat.send_message(user_msg)
        
        return {
            "status": "success",
            "message": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in career chat: {str(e)}")

@api_router.post("/ai/job-match")
async def get_job_recommendations(
    current_user: User = Depends(require_role([UserRole.STUDENT]))
):
    try:
        # Get student profile
        profile = await db.student_profiles.find_one({"user_id": current_user.id})
        if not profile:
            raise HTTPException(status_code=404, detail="Student profile not found")
        
        # Get all active jobs
        jobs = await db.jobs.find({"status": JobStatus.ACTIVE}).to_list(100)
        
        # Use AI to match jobs
        user_skills = profile.get("skills", [])
        user_degree = profile.get("degree", "")
        
        job_summaries = []
        for job in jobs[:20]:  # Limit for API efficiency
            job_summaries.append({
                "id": job["id"],
                "title": job["title"],
                "requirements": job.get("requirements", []),
                "description": job["description"][:200]  # Truncate for API
            })
        
        prompt = f"""
        Based on the student profile, recommend the most suitable jobs from the list below.
        
        Student Profile:
        - Skills: {', '.join(user_skills)}
        - Degree: {user_degree}
        
        Available Jobs:
        {json.dumps(job_summaries, indent=2)}
        
        Return a JSON array of job IDs ranked by suitability (best matches first), 
        along with match scores (0-100) and reasons. Format:
        [
          {{
            "job_id": "job_id_here",
            "match_score": 85,
            "reasons": ["Skill match: Python, React", "Experience level appropriate"]
          }}
        ]
        
        Return only the JSON array.
        """
        
        response = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        ai_response = response.choices[0].message.content
        
        try:
            recommendations = json.loads(ai_response)
        except json.JSONDecodeError:
            recommendations = []
        
        return {
            "status": "success",
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in job matching: {str(e)}")

    result = AssessmentResult(
        assessment_id=assessment_id,
        student_id=current_user.id,
        answers=result_data.get("answers", []),
        score=score,
        passed=passed
    )
    
    await db.assessment_results.insert_one(result.dict())
    return result

@api_router.get("/assessments/results/my", response_model=List[AssessmentResult])
async def get_my_assessment_results(current_user: User = Depends(require_role([UserRole.STUDENT]))):
    results = await db.assessment_results.find({"student_id": current_user.id}).to_list(100)
    return [AssessmentResult(**result) for result in results]

# Admin endpoints
@api_router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(current_user: User = Depends(require_role([UserRole.ADMIN]))):
    users = await db.users.find().to_list(1000)
    return [UserResponse(**user) for user in users]

@api_router.put("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_data: dict,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"role": role_data["role"], "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "User role updated successfully"}

@api_router.put("/admin/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status_data: dict,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"is_active": status_data["is_active"], "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "User status updated successfully"}

                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Placement AI API - Ready to serve!"}

# Authentication endpoints
@api_router.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = hash_password(user_data.password)
    user = User(
        **user_data.dict(exclude={'password'}),
        hashed_password=hashed_password
    )
    
    await db.users.insert_one(user.dict())
    
    # Create profile based on role
    if user.role == UserRole.STUDENT:
        profile = StudentProfile(user_id=user.id)
        await db.student_profiles.insert_one(profile.dict())
    elif user.role == UserRole.RECRUITER:
        # Company profile can be created later
        pass
    
    return UserResponse(**user.dict())

@api_router.post("/auth/login", response_model=Token)
async def login_user(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user)
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
