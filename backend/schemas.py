from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID
import uuid

# Base schemas
class BaseResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: Optional[str] = None

# Authentication schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(..., regex="^(student|faculty|recruiter|admin)$")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes in seconds

# User schemas
class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

# Student schemas
class StudentBase(BaseModel):
    department: str = Field(..., max_length=100)
    year: int = Field(..., ge=1, le=4)
    cgpa: Optional[Decimal] = Field(None, ge=0, le=10)
    skills: Optional[List[str]] = []
    resume_url: Optional[str] = None

class StudentCreate(StudentBase):
    user: UserRegister

class StudentUpdate(BaseModel):
    department: Optional[str] = None
    year: Optional[int] = Field(None, ge=1, le=4)
    cgpa: Optional[Decimal] = Field(None, ge=0, le=10)
    skills: Optional[List[str]] = None
    resume_url: Optional[str] = None
    eligibility_status: Optional[str] = Field(None, regex="^(pending|eligible|not_eligible)$")
    placement_status: Optional[str] = Field(None, regex="^(unplaced|placed|higher_studies|entrepreneurship)$")
    placed_company: Optional[str] = None
    placed_role: Optional[str] = None
    package_lpa: Optional[Decimal] = None

class StudentResponse(StudentBase):
    student_id: UUID
    user_id: UUID
    eligibility_status: str
    placement_status: str
    placed_company: Optional[str]
    placed_role: Optional[str]
    package_lpa: Optional[Decimal]
    placement_score: int
    user: UserResponse
    
    class Config:
        from_attributes = True

# Faculty schemas
class FacultyCreate(BaseModel):
    user: UserRegister
    department: str = Field(..., max_length=100)
    designation: str = Field(..., max_length=100)

class FacultyResponse(BaseModel):
    faculty_id: UUID
    user_id: UUID
    department: str
    designation: str
    user: UserResponse
    
    class Config:
        from_attributes = True

# Recruiter schemas
class RecruiterCreate(BaseModel):
    user: UserRegister
    company: str = Field(..., max_length=200)
    designation: str = Field(..., max_length=100)
    industry: Optional[str] = Field(None, max_length=100)

class RecruiterResponse(BaseModel):
    recruiter_id: UUID
    user_id: UUID
    company: str
    designation: str
    industry: Optional[str]
    user: UserResponse
    
    class Config:
        from_attributes = True

# Job schemas
class JobBase(BaseModel):
    title: str = Field(..., max_length=200)
    company: str = Field(..., max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    job_type: str = Field("full_time", regex="^(full_time|part_time|internship|contract)$")
    experience_level: str = Field("entry", regex="^(entry|mid|senior)$")
    required_skills: List[str] = []
    description: Optional[str] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    deadline: Optional[datetime] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = Field(None, regex="^(full_time|part_time|internship|contract)$")
    experience_level: Optional[str] = Field(None, regex="^(entry|mid|senior)$")
    required_skills: Optional[List[str]] = None
    description: Optional[str] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    deadline: Optional[datetime] = None
    is_active: Optional[bool] = None

class JobResponse(JobBase):
    job_id: UUID
    recruiter_id: UUID
    posted_date: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# Application schemas
class ApplicationCreate(BaseModel):
    job_id: UUID

class ApplicationUpdate(BaseModel):
    status: str = Field(..., regex="^(applied|shortlisted|interviewed|hired|rejected)$")

class ApplicationResponse(BaseModel):
    app_id: UUID
    job_id: UUID
    student_id: UUID
    status: str
    applied_date: datetime
    updated_date: datetime
    
    class Config:
        from_attributes = True

# Assessment schemas
class AssessmentCreate(BaseModel):
    type: str = Field(..., regex="^(mock_test|skill_test|interview)$")
    category: str = Field(..., max_length=100)
    score: int = Field(..., ge=0)
    total_questions: int = Field(..., gt=0)
    correct_answers: int = Field(..., ge=0)
    difficulty: str = Field("medium", regex="^(easy|medium|hard)$")
    feedback: Optional[str] = None
    recommendations: Optional[List[str]] = []
    duration_minutes: Optional[int] = None

    @validator('correct_answers')
    def correct_answers_must_not_exceed_total(cls, v, values):
        if 'total_questions' in values and v > values['total_questions']:
            raise ValueError('Correct answers cannot exceed total questions')
        return v

class AssessmentResponse(AssessmentCreate):
    assessment_id: UUID
    student_id: UUID
    assessment_date: datetime
    
    class Config:
        from_attributes = True

# Skill Analysis schemas
class SkillAnalysisCreate(BaseModel):
    skill_name: str = Field(..., max_length=100)
    category: str = Field(..., max_length=100)
    current_demand: int = 0
    predicted_demand: int = 0
    growth_rate: Decimal = 0
    industry_focus: List[str] = []
    trend: str = Field("stable", regex="^(rising|falling|stable)$")

class SkillAnalysisResponse(SkillAnalysisCreate):
    skill_id: UUID
    last_updated: datetime
    
    class Config:
        from_attributes = True

# Notification schemas
class NotificationCreate(BaseModel):
    message: str = Field(..., min_length=1)
    type: str = Field("info", regex="^(info|success|warning|error)$")

class NotificationResponse(NotificationCreate):
    notif_id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Document schemas
class DocumentCreate(BaseModel):
    type: str = Field(..., regex="^(resume|certificate|portfolio)$")
    file_name: str = Field(..., max_length=255)
    file_url: str = Field(..., max_length=500)
    file_size: Optional[int] = None

class DocumentResponse(DocumentCreate):
    doc_id: UUID
    student_id: UUID
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

# Analytics schemas
class PlacementStats(BaseModel):
    total_students: int
    total_placed: int
    placement_percentage: float
    average_package: Optional[Decimal]
    top_recruiters: List[Dict[str, Any]]

class SkillTrends(BaseModel):
    skill_name: str
    category: str
    trend: str
    growth_rate: Decimal
    current_demand: int
    predicted_demand: int

class DashboardData(BaseModel):
    placement_stats: PlacementStats
    recent_placements: List[Dict[str, Any]]
    skill_trends: List[SkillTrends]
    job_trends: List[Dict[str, Any]]
    notifications: List[NotificationResponse]

# File upload schemas
class FileUploadResponse(BaseModel):
    filename: str
    file_url: str
    file_size: int
    upload_date: datetime

# Bulk upload schemas
class BulkStudentUpload(BaseModel):
    students: List[Dict[str, Any]]
    
class BulkUploadResponse(BaseModel):
    total_records: int
    successful: int
    failed: int
    errors: List[Dict[str, str]]

# Search and filter schemas
class StudentFilter(BaseModel):
    department: Optional[str] = None
    year: Optional[int] = None
    placement_status: Optional[str] = None
    cgpa_min: Optional[Decimal] = None
    cgpa_max: Optional[Decimal] = None
    skills: Optional[List[str]] = []

class JobFilter(BaseModel):
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    skills: Optional[List[str]] = []
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None

# AI/ML schemas
class ResumeAnalysis(BaseModel):
    extracted_skills: List[str]
    experience_years: Optional[int]
    education: List[str]
    certifications: List[str]
    job_match_scores: List[Dict[str, Any]]

class CareerRecommendation(BaseModel):
    recommended_skills: List[str]
    job_matches: List[Dict[str, Any]]
    learning_path: List[str]
    estimated_salary_range: Dict[str, Decimal]