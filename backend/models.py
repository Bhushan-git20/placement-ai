from sqlalchemy import Column, String, Integer, Decimal, Boolean, DateTime, Text, ARRAY, JSON, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    students = relationship("Student", back_populates="user", cascade="all, delete-orphan")
    faculty = relationship("Faculty", back_populates="user", cascade="all, delete-orphan")
    recruiters = relationship("Recruiter", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("role IN ('student', 'faculty', 'recruiter', 'admin')", name="check_user_role"),
    )

class Student(Base):
    __tablename__ = "students"
    
    student_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    department = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    cgpa = Column(Decimal(4,2))
    skills = Column(JSONB, default=[])
    resume_url = Column(String(500))
    eligibility_status = Column(String(50), default="pending")
    placement_status = Column(String(50), default="unplaced", index=True)
    placed_company = Column(String(200))
    placed_role = Column(String(200))
    package_lpa = Column(Decimal(10,2))
    placement_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="students")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="student", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="student", cascade="all, delete-orphan")
    company_placements = relationship("CompanyPlacement", back_populates="student")
    
    __table_args__ = (
        CheckConstraint("year BETWEEN 1 AND 4", name="check_student_year"),
        CheckConstraint("cgpa >= 0 AND cgpa <= 10", name="check_student_cgpa"),
        CheckConstraint("eligibility_status IN ('pending', 'eligible', 'not_eligible')", name="check_eligibility_status"),
        CheckConstraint("placement_status IN ('unplaced', 'placed', 'higher_studies', 'entrepreneurship')", name="check_placement_status"),
    )

class Faculty(Base):
    __tablename__ = "faculty"
    
    faculty_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="faculty")

class Recruiter(Base):
    __tablename__ = "recruiters"
    
    recruiter_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company = Column(String(200), nullable=False)
    designation = Column(String(100), nullable=False)
    industry = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recruiters")
    jobs = relationship("Job", back_populates="recruiter", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"
    
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recruiter_id = Column(UUID(as_uuid=True), ForeignKey("recruiters.recruiter_id"), nullable=False)
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False, index=True)
    location = Column(String(200))
    job_type = Column(String(50), default="full_time")
    experience_level = Column(String(50), default="entry")
    required_skills = Column(ARRAY(Text), default=[])
    description = Column(Text)
    salary_min = Column(Decimal(10,2))
    salary_max = Column(Decimal(10,2))
    posted_date = Column(DateTime(timezone=True), server_default=func.now())
    deadline = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    recruiter = relationship("Recruiter", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("job_type IN ('full_time', 'part_time', 'internship', 'contract')", name="check_job_type"),
        CheckConstraint("experience_level IN ('entry', 'mid', 'senior')", name="check_experience_level"),
    )

class Application(Base):
    __tablename__ = "applications"
    
    app_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.job_id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id"), nullable=False)
    status = Column(String(50), default="applied", index=True)
    applied_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    student = relationship("Student", back_populates="applications")
    
    __table_args__ = (
        CheckConstraint("status IN ('applied', 'shortlisted', 'interviewed', 'hired', 'rejected')", name="check_application_status"),
    )

class Assessment(Base):
    __tablename__ = "assessments"
    
    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    difficulty = Column(String(20), default="medium")
    feedback = Column(Text)
    recommendations = Column(ARRAY(Text), default=[])
    assessment_date = Column(DateTime(timezone=True), server_default=func.now())
    duration_minutes = Column(Integer)
    
    # Relationships
    student = relationship("Student", back_populates="assessments")
    
    __table_args__ = (
        CheckConstraint("type IN ('mock_test', 'skill_test', 'interview')", name="check_assessment_type"),
        CheckConstraint("difficulty IN ('easy', 'medium', 'hard')", name="check_assessment_difficulty"),
        CheckConstraint("score >= 0", name="check_assessment_score"),
        CheckConstraint("total_questions > 0", name="check_total_questions"),
        CheckConstraint("correct_answers >= 0", name="check_correct_answers"),
    )

class SkillAnalysis(Base):
    __tablename__ = "skill_analysis"
    
    skill_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), nullable=False)
    current_demand = Column(Integer, default=0)
    predicted_demand = Column(Integer, default=0)
    growth_rate = Column(Decimal(5,2), default=0)
    industry_focus = Column(ARRAY(Text), default=[])
    trend = Column(String(20), default="stable", index=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("trend IN ('rising', 'falling', 'stable')", name="check_skill_trend"),
    )

class Notification(Base):
    __tablename__ = "notifications"
    
    notif_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")
    status = Column(String(20), default="unread", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    __table_args__ = (
        CheckConstraint("type IN ('info', 'success', 'warning', 'error')", name="check_notification_type"),
        CheckConstraint("status IN ('read', 'unread')", name="check_notification_status"),
    )

class Document(Base):
    __tablename__ = "documents"
    
    doc_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id"), nullable=False)
    type = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="documents")
    
    __table_args__ = (
        CheckConstraint("type IN ('resume', 'certificate', 'portfolio')", name="check_document_type"),
    )

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSONB, default={})
    ip_address = Column(INET)
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")

class CompanyPlacement(Base):
    __tablename__ = "company_placements"
    
    placement_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id"), nullable=False)
    company = Column(String(200), nullable=False)
    role = Column(String(200), nullable=False)
    package_lpa = Column(Decimal(10,2))
    placement_date = Column(DateTime(timezone=True), server_default=func.now())
    academic_year = Column(String(10))
    department = Column(String(100))
    
    # Relationships
    student = relationship("Student", back_populates="company_placements")