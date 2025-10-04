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
from emergentintegrations.llm.chat import LlmChat, UserMessage
import base64
import io

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Placement AI API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("SECRET_KEY", "placement-ai-secret-key-change-in-production")
ALGORITHM = "HS256"

# AI Integration
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "sk-emergent-b4aC635415a2959C20")

# Enums for User Roles
class UserRole(str, Enum):
    STUDENT = "student"
    RECRUITER = "recruiter"
    FACULTY = "faculty"
    ADMIN = "admin"

class JobStatus(str, Enum):
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
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# API Routes
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
        ai_response = await chat.send_message(user_message)
        
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