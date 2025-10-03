from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import os
import json
import pandas as pd
from io import StringIO

# Import all models and schemas
from models import *
from schemas import *
from database import get_db, engine
from auth import (
    auth_handler, get_current_user, get_current_active_user,
    require_admin, require_student, require_faculty, require_recruiter,
    require_student_or_faculty
)

# Create FastAPI app
app = FastAPI(
    title="PlacePredict: AI-Powered Placement Analysis System",
    description="Complete placement management system with AI-powered analytics",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router with prefix
api_router = APIRouter(prefix="/api")

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# =======================
# AUTHENTICATION ROUTES
# =======================

@api_router.post("/auth/register", response_model=BaseResponse)
async def register_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = auth_handler.get_password_hash(user_data.password)
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return BaseResponse(
        message="User registered successfully",
        data={"user_id": str(new_user.id), "role": new_user.role}
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login_user(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return tokens"""
    # Get user by email
    result = await db.execute(select(User).where(User.email == user_credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not auth_handler.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Create tokens
    access_token = auth_handler.create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = auth_handler.create_refresh_token({"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

# =======================
# STUDENT ROUTES
# =======================

@api_router.post("/students", response_model=BaseResponse)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_faculty)
):
    """Create a new student (Faculty/Admin only)"""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == student_data.user.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = auth_handler.get_password_hash(student_data.user.password)
    new_user = User(
        full_name=student_data.user.full_name,
        email=student_data.user.email,
        password_hash=hashed_password,
        role="student"
    )
    db.add(new_user)
    await db.flush()
    
    # Create student
    new_student = Student(
        user_id=new_user.id,
        department=student_data.department,
        year=student_data.year,
        cgpa=student_data.cgpa,
        skills=student_data.skills or [],
        resume_url=student_data.resume_url
    )
    db.add(new_student)
    await db.commit()
    
    return BaseResponse(message="Student created successfully")

@api_router.get("/students", response_model=List[StudentResponse])
async def get_students(
    skip: int = 0,
    limit: int = 100,
    department: Optional[str] = None,
    year: Optional[int] = None,
    placement_status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_student_or_faculty)
):
    """Get list of students with filters"""
    query = select(Student).options(selectinload(Student.user))
    
    # Apply filters
    if department:
        query = query.where(Student.department == department)
    if year:
        query = query.where(Student.year == year)
    if placement_status:
        query = query.where(Student.placement_status == placement_status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    students = result.scalars().all()
    
    return [StudentResponse.from_orm(student) for student in students]

@api_router.get("/students/me", response_model=StudentResponse)
async def get_my_profile(
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    """Get current student's profile"""
    result = await db.execute(
        select(Student).options(selectinload(Student.user)).where(Student.user_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    return StudentResponse.from_orm(student)

@api_router.put("/students/me", response_model=BaseResponse)
async def update_my_profile(
    student_update: StudentUpdate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    """Update current student's profile"""
    result = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Update student fields
    for field, value in student_update.dict(exclude_unset=True).items():
        setattr(student, field, value)
    
    await db.commit()
    return BaseResponse(message="Profile updated successfully")

# =======================
# JOB ROUTES
# =======================

@api_router.post("/jobs", response_model=BaseResponse)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
):
    """Create a new job posting"""
    # Get recruiter profile
    result = await db.execute(select(Recruiter).where(Recruiter.user_id == current_user.id))
    recruiter = result.scalar_one_or_none()
    
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter profile not found")
    
    new_job = Job(
        recruiter_id=recruiter.recruiter_id,
        **job_data.dict()
    )
    
    db.add(new_job)
    await db.commit()
    return BaseResponse(message="Job posted successfully")

@api_router.get("/jobs", response_model=List[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    company: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of jobs with filters"""
    query = select(Job)
    
    # Apply filters
    if company:
        query = query.where(Job.company.ilike(f"%{company}%"))
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))
    if job_type:
        query = query.where(Job.job_type == job_type)
    
    query = query.where(Job.is_active == is_active)
    query = query.offset(skip).limit(limit).order_by(desc(Job.posted_date))
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return [JobResponse.from_orm(job) for job in jobs]

@api_router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get job details by ID"""
    result = await db.execute(select(Job).where(Job.job_id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse.from_orm(job)

# =======================
# APPLICATION ROUTES
# =======================

@api_router.post("/applications", response_model=BaseResponse)
async def apply_for_job(
    application_data: ApplicationCreate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    """Apply for a job"""
    # Get student profile
    result = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Check if already applied
    result = await db.execute(
        select(Application).where(
            and_(Application.job_id == application_data.job_id, Application.student_id == student.student_id)
        )
    )
    existing_application = result.scalar_one_or_none()
    
    if existing_application:
        raise HTTPException(status_code=400, detail="Already applied for this job")
    
    # Check if job exists and is active
    result = await db.execute(select(Job).where(Job.job_id == application_data.job_id))
    job = result.scalar_one_or_none()
    
    if not job or not job.is_active:
        raise HTTPException(status_code=404, detail="Job not found or inactive")
    
    # Create application
    new_application = Application(
        job_id=application_data.job_id,
        student_id=student.student_id,
        status="applied"
    )
    
    db.add(new_application)
    await db.commit()
    
    return BaseResponse(message="Application submitted successfully")

@api_router.get("/applications/me", response_model=List[ApplicationResponse])
async def get_my_applications(
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    """Get current student's applications"""
    # Get student profile
    result = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    result = await db.execute(
        select(Application).where(Application.student_id == student.student_id).order_by(desc(Application.applied_date))
    )
    applications = result.scalars().all()
    
    return [ApplicationResponse.from_orm(app) for app in applications]

# =======================
# ASSESSMENT ROUTES
# =======================

@api_router.post("/assessments", response_model=BaseResponse)
async def create_assessment(
    assessment_data: AssessmentCreate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    """Create/submit an assessment"""
    # Get student profile
    result = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    new_assessment = Assessment(
        student_id=student.student_id,
        **assessment_data.dict()
    )
    
    db.add(new_assessment)
    await db.commit()
    
    return BaseResponse(message="Assessment submitted successfully")

@api_router.get("/assessments/me", response_model=List[AssessmentResponse])
async def get_my_assessments(
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db)
):
    """Get current student's assessments"""
    # Get student profile
    result = await db.execute(select(Student).where(Student.user_id == current_user.id))
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    result = await db.execute(
        select(Assessment).where(Assessment.student_id == student.student_id).order_by(desc(Assessment.assessment_date))
    )
    assessments = result.scalars().all()
    
    return [AssessmentResponse.from_orm(assessment) for assessment in assessments]

# =======================
# SKILL ANALYSIS ROUTES
# =======================

@api_router.get("/skills/trending", response_model=List[SkillAnalysisResponse])
async def get_trending_skills(
    limit: int = 20,
    trend: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get trending skills"""
    query = select(SkillAnalysis).order_by(desc(SkillAnalysis.growth_rate))
    
    if trend:
        query = query.where(SkillAnalysis.trend == trend)
    
    query = query.limit(limit)
    result = await db.execute(query)
    skills = result.scalars().all()
    
    return [SkillAnalysisResponse.from_orm(skill) for skill in skills]

# =======================
# DASHBOARD ROUTES
# =======================

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics"""
    # Total students
    total_students_result = await db.execute(select(func.count(Student.student_id)))
    total_students = total_students_result.scalar()
    
    # Total placed students
    placed_students_result = await db.execute(
        select(func.count(Student.student_id)).where(Student.placement_status == "placed")
    )
    total_placed = placed_students_result.scalar()
    
    # Average package
    avg_package_result = await db.execute(
        select(func.avg(Student.package_lpa)).where(Student.placement_status == "placed")
    )
    avg_package = avg_package_result.scalar()
    
    # Top recruiters
    top_recruiters_result = await db.execute(
        select(Student.placed_company, func.count(Student.student_id).label('count'))
        .where(Student.placement_status == "placed")
        .group_by(Student.placed_company)
        .order_by(desc('count'))
        .limit(5)
    )
    top_recruiters = [{"company": row[0], "count": row[1]} for row in top_recruiters_result.fetchall()]
    
    # Recent placements
    recent_placements_result = await db.execute(
        select(Student).options(selectinload(Student.user))
        .where(Student.placement_status == "placed")
        .order_by(desc(Student.updated_at))
        .limit(5)
    )
    recent_placements = recent_placements_result.scalars().all()
    
    # Trending skills
    trending_skills_result = await db.execute(
        select(SkillAnalysis).order_by(desc(SkillAnalysis.growth_rate)).limit(5)
    )
    trending_skills = trending_skills_result.scalars().all()
    
    return {
        "placement_stats": {
            "total_students": total_students,
            "total_placed": total_placed,
            "placement_percentage": (total_placed / total_students * 100) if total_students > 0 else 0,
            "average_package": float(avg_package) if avg_package else 0,
            "top_recruiters": top_recruiters
        },
        "recent_placements": [
            {
                "student_name": placement.user.full_name,
                "company": placement.placed_company,
                "role": placement.placed_role,
                "package": float(placement.package_lpa) if placement.package_lpa else 0
            }
            for placement in recent_placements
        ],
        "trending_skills": [
            {
                "skill_name": skill.skill_name,
                "growth_rate": float(skill.growth_rate),
                "trend": skill.trend
            }
            for skill in trending_skills
        ]
    }

# =======================
# NOTIFICATION ROUTES
# =======================

@api_router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user notifications"""
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if status_filter:
        query = query.where(Notification.status == status_filter)
    
    query = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return [NotificationResponse.from_orm(notif) for notif in notifications]

@api_router.put("/notifications/{notif_id}/read", response_model=BaseResponse)
async def mark_notification_read(
    notif_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read"""
    result = await db.execute(
        select(Notification).where(
            and_(Notification.notif_id == notif_id, Notification.user_id == current_user.id)
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.status = "read"
    await db.commit()
    
    return BaseResponse(message="Notification marked as read")

# =======================
# ADMIN ROUTES
# =======================

@api_router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (Admin only)"""
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    
    query = query.offset(skip).limit(limit).order_by(User.created_at)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [UserResponse.from_orm(user) for user in users]

@api_router.put("/admin/users/{user_id}/role", response_model=BaseResponse)
async def update_user_role(
    user_id: UUID,
    role_data: dict,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update user role (Admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_role = role_data.get("role")
    if new_role not in ["student", "faculty", "recruiter", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user.role = new_role
    await db.commit()
    
    return BaseResponse(message="User role updated successfully")

# Include the router in the app
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "PlacePredict API", "status": "running", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)