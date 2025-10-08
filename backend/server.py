from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

# Student Profile Models
class Education(BaseModel):
    degree: str
    university: str
    year: int
    gpa: Optional[float] = None

class Experience(BaseModel):
    company: str
    role: str
    duration: str
    description: str

class Skill(BaseModel):
    name: str
    proficiency: str  # beginner, intermediate, advanced, expert

class StudentProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    phone: str
    education: List[Education] = []
    skills: List[Skill] = []
    experience: List[Experience] = []
    resume_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StudentProfileCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    education: List[Education] = []
    skills: List[Skill] = []
    experience: List[Experience] = []

class StudentProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    education: Optional[List[Education]] = None
    skills: Optional[List[Skill]] = None
    experience: Optional[List[Experience]] = None

# Job Models
class Job(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    company: str
    description: str
    requirements: List[str]
    location: str
    salary_range: Optional[str] = None
    job_type: str  # full-time, part-time, internship, contract
    posted_date: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    requirements: List[str]
    location: str
    salary_range: Optional[str] = None
    job_type: str

# Application Models
class Application(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    job_id: str
    status: str = "submitted"  # submitted, under_review, shortlisted, rejected, accepted
    applied_date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class ApplicationCreate(BaseModel):
    student_id: str
    job_id: str
    notes: Optional[str] = None

# Test Models
class Question(BaseModel):
    question: str
    options: List[str]
    correct_answer: int  # index of correct option

class Test(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: str
    duration_minutes: int
    questions: List[Question]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TestCreate(BaseModel):
    title: str
    description: str
    category: str
    duration_minutes: int
    questions: List[Question]

class TestAnswer(BaseModel):
    question_index: int
    selected_answer: int

class TestSubmission(BaseModel):
    student_id: str
    test_id: str
    answers: List[TestAnswer]

class TestResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    test_id: str
    score: float
    total_questions: int
    correct_answers: int
    answers: List[TestAnswer]
    completed_at: datetime = Field(default_factory=datetime.utcnow)

# Interview Question Models
class InterviewQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    category: str
    difficulty: str  # easy, medium, hard
    skills: List[str]

class InterviewQuestionCreate(BaseModel):
    question: str
    category: str
    difficulty: str
    skills: List[str]

# AI Models
class SkillGap(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    missing_skills: List[str]
    recommended_courses: List[str]
    ai_analysis: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class JobMatch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    job_id: str
    match_score: float
    ai_reasoning: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ==================== HELPER FUNCTIONS ====================

async def get_ai_chat():
    """Initialize AI chat with Emergent LLM key"""
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    chat = LlmChat(
        api_key=api_key,
        session_id=str(uuid.uuid4()),
        system_message="You are an AI career advisor specializing in job matching and skill gap analysis."
    ).with_model("openai", "gpt-4o-mini")
    return chat

# ==================== STUDENT PROFILE ENDPOINTS ====================

@api_router.post("/students", response_model=StudentProfile)
async def create_student_profile(student: StudentProfileCreate):
    """Create a new student profile"""
    try:
        student_dict = student.dict()
        student_obj = StudentProfile(**student_dict)
        await db.students.insert_one(student_obj.dict())
        logger.info(f"Created student profile: {student_obj.id}")
        return student_obj
    except Exception as e:
        logger.error(f"Error creating student profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/students/{student_id}", response_model=StudentProfile)
async def get_student_profile(student_id: str):
    """Get a student profile by ID"""
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentProfile(**student)

@api_router.get("/students", response_model=List[StudentProfile])
async def get_all_students():
    """Get all student profiles"""
    students = await db.students.find().to_list(1000)
    return [StudentProfile(**student) for student in students]

@api_router.put("/students/{student_id}", response_model=StudentProfile)
async def update_student_profile(student_id: str, updates: StudentProfileUpdate):
    """Update a student profile"""
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    await db.students.update_one({"id": student_id}, {"$set": update_data})

    updated_student = await db.students.find_one({"id": student_id})
    return StudentProfile(**updated_student)

@api_router.post("/students/{student_id}/resume")
async def upload_resume(student_id: str, resume_text: str = Form(...)):
    """Upload or update student resume (storing as text for simplicity)"""
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Store resume text in the profile
    await db.students.update_one(
        {"id": student_id},
        {"$set": {"resume_url": resume_text, "updated_at": datetime.utcnow()}}
    )

    return {"message": "Resume uploaded successfully", "student_id": student_id}

@api_router.delete("/students/{student_id}")
async def delete_student_profile(student_id: str):
    """Delete a student profile"""
    result = await db.students.delete_one({"id": student_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student profile deleted successfully"}

# ==================== JOB ENDPOINTS ====================

@api_router.post("/jobs", response_model=Job)
async def create_job(job: JobCreate):
    """Create a new job listing"""
    try:
        job_obj = Job(**job.dict())
        await db.jobs.insert_one(job_obj.dict())
        logger.info(f"Created job: {job_obj.id}")
        return job_obj
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/jobs", response_model=List[Job])
async def get_all_jobs(active_only: bool = True):
    """Get all job listings"""
    query = {"is_active": True} if active_only else {}
    jobs = await db.jobs.find(query).to_list(1000)
    return [Job(**job) for job in jobs]

@api_router.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get a specific job by ID"""
    job = await db.jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return Job(**job)

@api_router.put("/jobs/{job_id}", response_model=Job)
async def update_job(job_id: str, job_update: JobCreate):
    """Update a job listing"""
    job = await db.jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    await db.jobs.update_one({"id": job_id}, {"$set": job_update.dict()})
    updated_job = await db.jobs.find_one({"id": job_id})
    return Job(**updated_job)

@api_router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job listing"""
    result = await db.jobs.delete_one({"id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

# ==================== APPLICATION ENDPOINTS ====================

@api_router.post("/applications", response_model=Application)
async def submit_application(application: ApplicationCreate):
    """Submit a job application"""
    try:
        # Verify student and job exist
        student = await db.students.find_one({"id": application.student_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        job = await db.jobs.find_one({"id": application.job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Check if already applied
        existing = await db.applications.find_one({
            "student_id": application.student_id,
            "job_id": application.job_id
        })
        if existing:
            raise HTTPException(status_code=400, detail="Already applied to this job")

        app_obj = Application(**application.dict())
        await db.applications.insert_one(app_obj.dict())
        logger.info(f"Application submitted: {app_obj.id}")
        return app_obj
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/applications/student/{student_id}", response_model=List[Application])
async def get_student_applications(student_id: str):
    """Get all applications for a student"""
    applications = await db.applications.find({"student_id": student_id}).to_list(1000)
    return [Application(**app) for app in applications]

@api_router.get("/applications", response_model=List[Application])
async def get_all_applications():
    """Get all applications"""
    applications = await db.applications.find().to_list(1000)
    return [Application(**app) for app in applications]

@api_router.put("/applications/{application_id}/status")
async def update_application_status(application_id: str, status: str):
    """Update application status"""
    valid_statuses = ["submitted", "under_review", "shortlisted", "rejected", "accepted"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    result = await db.applications.update_one(
        {"id": application_id},
        {"$set": {"status": status}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")

    return {"message": "Application status updated successfully", "status": status}

# ==================== TEST ENDPOINTS ====================

@api_router.post("/tests", response_model=Test)
async def create_test(test: TestCreate):
    """Create a new test"""
    try:
        test_obj = Test(**test.dict())
        await db.tests.insert_one(test_obj.dict())
        logger.info(f"Created test: {test_obj.id}")
        return test_obj
    except Exception as e:
        logger.error(f"Error creating test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tests", response_model=List[Test])
async def get_all_tests():
    """Get all tests"""
    tests = await db.tests.find().to_list(1000)
    return [Test(**test) for test in tests]

@api_router.get("/tests/{test_id}", response_model=Test)
async def get_test(test_id: str):
    """Get a specific test by ID"""
    test = await db.tests.find_one({"id": test_id})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return Test(**test)

@api_router.post("/tests/submit", response_model=TestResult)
async def submit_test(submission: TestSubmission):
    """Submit test answers and calculate score"""
    try:
        # Get the test
        test = await db.tests.find_one({"id": submission.test_id})
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")

        test_obj = Test(**test)

        # Calculate score
        correct_answers = 0
        total_questions = len(test_obj.questions)

        for answer in submission.answers:
            if answer.question_index < total_questions:
                correct_answer = test_obj.questions[answer.question_index].correct_answer
                if answer.selected_answer == correct_answer:
                    correct_answers += 1

        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

        # Create test result
        result = TestResult(
            student_id=submission.student_id,
            test_id=submission.test_id,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers,
            answers=submission.answers
        )

        await db.test_results.insert_one(result.dict())
        logger.info(f"Test result saved: {result.id}, Score: {score}%")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/test-results/student/{student_id}", response_model=List[TestResult])
async def get_student_test_results(student_id: str):
    """Get all test results for a student"""
    results = await db.test_results.find({"student_id": student_id}).to_list(1000)
    return [TestResult(**result) for result in results]

# ==================== INTERVIEW QUESTIONS ENDPOINTS ====================

@api_router.post("/interview-questions/seed")
async def seed_interview_questions():
    """Seed the database with sample interview questions"""
    sample_questions = [
        {
            "question": "What is polymorphism in object-oriented programming?",
            "category": "Programming",
            "difficulty": "medium",
            "skills": ["OOP", "Programming Fundamentals"]
        },
        {
            "question": "Explain the difference between SQL and NoSQL databases.",
            "category": "Database",
            "difficulty": "medium",
            "skills": ["Database", "SQL", "NoSQL"]
        },
        {
            "question": "What is the time complexity of binary search?",
            "category": "Data Structures & Algorithms",
            "difficulty": "easy",
            "skills": ["Algorithms", "Data Structures"]
        },
        {
            "question": "Describe the concept of RESTful APIs.",
            "category": "Web Development",
            "difficulty": "medium",
            "skills": ["API Design", "Web Development"]
        },
        {
            "question": "What is the difference between let, var, and const in JavaScript?",
            "category": "Programming",
            "difficulty": "easy",
            "skills": ["JavaScript", "Programming"]
        },
        {
            "question": "Explain the CAP theorem in distributed systems.",
            "category": "System Design",
            "difficulty": "hard",
            "skills": ["System Design", "Distributed Systems"]
        },
        {
            "question": "What is dependency injection?",
            "category": "Software Engineering",
            "difficulty": "medium",
            "skills": ["Design Patterns", "Software Engineering"]
        },
        {
            "question": "How does HTTPS ensure secure communication?",
            "category": "Security",
            "difficulty": "medium",
            "skills": ["Security", "Networking"]
        },
        {
            "question": "What are microservices and their advantages?",
            "category": "Architecture",
            "difficulty": "hard",
            "skills": ["System Design", "Architecture"]
        },
        {
            "question": "Explain the concept of virtual DOM in React.",
            "category": "Frontend",
            "difficulty": "medium",
            "skills": ["React", "Frontend Development"]
        }
    ]

    # Clear existing questions
    await db.interview_questions.delete_many({})

    # Insert new questions
    questions = [InterviewQuestion(**q) for q in sample_questions]
    await db.interview_questions.insert_many([q.dict() for q in questions])

    return {"message": f"Seeded {len(questions)} interview questions successfully"}

@api_router.post("/interview-questions", response_model=InterviewQuestion)
async def create_interview_question(question: InterviewQuestionCreate):
    """Create a new interview question"""
    question_obj = InterviewQuestion(**question.dict())
    await db.interview_questions.insert_one(question_obj.dict())
    return question_obj

@api_router.get("/interview-questions", response_model=List[InterviewQuestion])
async def get_interview_questions(category: Optional[str] = None, difficulty: Optional[str] = None):
    """Get interview questions with optional filters"""
    query = {}
    if category:
        query["category"] = category
    if difficulty:
        query["difficulty"] = difficulty

    questions = await db.interview_questions.find(query).to_list(1000)
    return [InterviewQuestion(**q) for q in questions]

# ==================== AI JOB MATCHING ENDPOINTS ====================

@api_router.post("/ai/job-match/{student_id}")
async def generate_job_matches(student_id: str):
    """Generate AI-powered job matches for a student"""
    try:
        # Get student profile
        student = await db.students.find_one({"id": student_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        student_obj = StudentProfile(**student)

        # Get all active jobs
        jobs = await db.jobs.find({"is_active": True}).to_list(100)
        if not jobs:
            return {"message": "No active jobs available"}

        # Clear old matches for this student
        await db.job_matches.delete_many({"student_id": student_id})

        matches = []

        for job_data in jobs:
            job_obj = Job(**job_data)

            # Prepare AI prompt
            student_skills = ", ".join([s.name for s in student_obj.skills])
            job_requirements = ", ".join(job_obj.requirements)

            prompt = f"""
Analyze the match between this student and job:

Student Skills: {student_skills}
Student Education: {[f"{e.degree} from {e.university}" for e in student_obj.education]}

Job Title: {job_obj.title}
Job Requirements: {job_requirements}
Job Description: {job_obj.description}

Provide:
1. A match score from 0-100
2. Brief reasoning (2-3 sentences)

Format your response as JSON:
{{"score": <number>, "reasoning": "<text>"}}
"""

            try:
                chat = await get_ai_chat()
                message = UserMessage(text=prompt)
                response = await chat.send_message(message)

                # Parse AI response
                response_text = response.strip()
                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "").replace("```", "").strip()

                ai_result = json.loads(response_text)
                score = float(ai_result.get("score", 0))
                reasoning = ai_result.get("reasoning", "No reasoning provided")

                # Create match record
                match = JobMatch(
                    student_id=student_id,
                    job_id=job_obj.id,
                    match_score=score,
                    ai_reasoning=reasoning
                )

                await db.job_matches.insert_one(match.dict())
                matches.append(match)

            except Exception as e:
                logger.error(f"Error processing job match for job {job_obj.id}: {str(e)}")
                continue

        logger.info(f"Generated {len(matches)} job matches for student {student_id}")
        return {
            "message": f"Generated {len(matches)} job matches",
            "matches": [m.dict() for m in matches]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating job matches: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/ai/job-match/{student_id}", response_model=List[JobMatch])
async def get_job_matches(student_id: str):
    """Get AI-generated job matches for a student"""
    matches = await db.job_matches.find({"student_id": student_id}).sort("match_score", -1).to_list(100)
    return [JobMatch(**match) for match in matches]

@api_router.post("/ai/skill-gap/{student_id}")
async def analyze_skill_gap(student_id: str):
    """Analyze skill gaps for a student based on job market"""
    try:
        # Get student profile
        student = await db.students.find_one({"id": student_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        student_obj = StudentProfile(**student)

        # Get all active jobs
        jobs = await db.jobs.find({"is_active": True}).to_list(100)

        # Collect all required skills from jobs
        all_job_requirements = []
        for job in jobs:
            all_job_requirements.extend(Job(**job).requirements)

        student_skills = [s.name for s in student_obj.skills]

        # Prepare AI prompt
        prompt = f"""
Analyze skill gaps for this student based on current job market:

Student's Current Skills: {", ".join(student_skills) if student_skills else "No skills listed"}

Job Market Requirements (from {len(jobs)} jobs): {", ".join(set(all_job_requirements)) if all_job_requirements else "Various technical skills"}

IMPORTANT: Format your response as valid JSON with these EXACT field types:
- missing_skills: array of STRING values (not objects)
- recommended_courses: array of STRING values (not objects)
- analysis: a single STRING value

Example response format:
{{
  "missing_skills": ["Docker", "Kubernetes", "AWS"],
  "recommended_courses": ["Docker Mastery Course", "AWS Certified Solutions Architect", "Kubernetes for Beginners"],
  "analysis": "Based on the job market analysis, you are missing several critical DevOps and cloud skills."
}}

Provide your analysis now in this exact JSON format:
"""

        chat = await get_ai_chat()
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)

        # Parse AI response with better error handling
        response_text = response.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()

        try:
            ai_result = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {response_text}")
            # Provide fallback response
            ai_result = {
                "missing_skills": ["Cloud Computing", "DevOps", "System Design"],
                "recommended_courses": ["AWS Cloud Practitioner", "Docker and Kubernetes", "System Design Interview Prep"],
                "analysis": "Unable to perform detailed analysis at this time. These are general recommendations based on market trends."
            }

        # Ensure the arrays contain only strings
        if isinstance(ai_result.get("missing_skills"), list):
            ai_result["missing_skills"] = [str(skill) if isinstance(skill, str) else str(skill.get("name", skill)) for skill in ai_result["missing_skills"]]
        else:
            ai_result["missing_skills"] = []

        if isinstance(ai_result.get("recommended_courses"), list):
            ai_result["recommended_courses"] = [str(course) if isinstance(course, str) else str(course.get("name", course)) for course in ai_result["recommended_courses"]]
        else:
            ai_result["recommended_courses"] = []

        # Create skill gap record
        skill_gap = SkillGap(
            student_id=student_id,
            missing_skills=ai_result.get("missing_skills", []),
            recommended_courses=ai_result.get("recommended_courses", []),
            ai_analysis=ai_result.get("analysis", "No analysis provided")
        )

        # Clear old skill gap analysis
        await db.skill_gaps.delete_many({"student_id": student_id})
        await db.skill_gaps.insert_one(skill_gap.dict())

        logger.info(f"Generated skill gap analysis for student {student_id}")
        return skill_gap

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing skill gap: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/ai/skill-gap/{student_id}", response_model=SkillGap)
async def get_skill_gap(student_id: str):
    """Get skill gap analysis for a student"""
    skill_gap = await db.skill_gaps.find_one({"student_id": student_id})
    if not skill_gap:
        raise HTTPException(status_code=404, detail="No skill gap analysis found. Generate one first.")
    return SkillGap(**skill_gap)

@api_router.post("/ai/job-recommendations/{student_id}")
async def get_job_recommendations(student_id: str, limit: int = 5):
    """Get top AI-recommended jobs for a student"""
    try:
        # First, generate matches if they don't exist
        existing_matches = await db.job_matches.find({"student_id": student_id}).to_list(1)
        if not existing_matches:
            await generate_job_matches(student_id)

        # Get top matches
        matches = await db.job_matches.find({"student_id": student_id}).sort("match_score", -1).limit(limit).to_list(limit)

        # Enrich with job details
        recommendations = []
        for match in matches:
            job = await db.jobs.find_one({"id": match["job_id"]})
            if job:
                recommendations.append({
                    "job": Job(**job).dict(),
                    "match_score": match["match_score"],
                    "ai_reasoning": match["ai_reasoning"]
                })

        return {
            "student_id": student_id,
            "recommendations": recommendations
        }

    except Exception as e:
        logger.error(f"Error getting job recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS DASHBOARD ENDPOINT ====================

@api_router.get("/analytics/student/{student_id}")
async def get_student_analytics(student_id: str):
    """Get comprehensive analytics for a student"""
    try:
        # Verify student exists
        student = await db.students.find_one({"id": student_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Get applications
        applications = await db.applications.find({"student_id": student_id}).to_list(1000)
        total_applications = len(applications)

        # Application status breakdown
        status_breakdown = {}
        for app in applications:
            status = app.get("status", "unknown")
            status_breakdown[status] = status_breakdown.get(status, 0) + 1

        # Get test results
        test_results = await db.test_results.find({"student_id": student_id}).to_list(1000)
        total_tests = len(test_results)
        average_test_score = sum([r["score"] for r in test_results]) / total_tests if total_tests > 0 else 0

        # Get job matches
        job_matches = await db.job_matches.find({"student_id": student_id}).sort("match_score", -1).limit(5).to_list(5)
        top_matches = []
        for match in job_matches:
            job = await db.jobs.find_one({"id": match["job_id"]})
            if job:
                top_matches.append({
                    "job_title": job["title"],
                    "company": job["company"],
                    "match_score": match["match_score"]
                })

        # Get skill gap
        skill_gap = await db.skill_gaps.find_one({"student_id": student_id})
        skill_gap_summary = None
        if skill_gap:
            skill_gap_summary = {
                "missing_skills": skill_gap.get("missing_skills", []),
                "recommended_courses": skill_gap.get("recommended_courses", [])
            }

        # Calculate success rate
        accepted_count = status_breakdown.get("accepted", 0)
        success_rate = (accepted_count / total_applications * 100) if total_applications > 0 else 0

        analytics = {
            "student_id": student_id,
            "total_applications": total_applications,
            "application_status_breakdown": status_breakdown,
            "total_tests_taken": total_tests,
            "average_test_score": round(average_test_score, 2),
            "top_job_matches": top_matches,
            "skill_gap_summary": skill_gap_summary,
            "application_success_rate": round(success_rate, 2)
        }

        logger.info(f"Generated analytics for student {student_id}")
        return analytics

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/overview")
async def get_platform_overview():
    """Get overall platform analytics"""
    try:
        total_students = await db.students.count_documents({})
        total_jobs = await db.jobs.count_documents({"is_active": True})
        total_applications = await db.applications.count_documents({})
        total_tests = await db.tests.count_documents({})

        # Application status breakdown
        all_applications = await db.applications.find().to_list(10000)
        status_breakdown = {}
        for app in all_applications:
            status = app.get("status", "unknown")
            status_breakdown[status] = status_breakdown.get(status, 0) + 1

        overview = {
            "total_students": total_students,
            "total_active_jobs": total_jobs,
            "total_applications": total_applications,
            "total_tests_available": total_tests,
            "application_status_breakdown": status_breakdown
        }

        return overview

    except Exception as e:
        logger.error(f"Error generating platform overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ROOT ENDPOINT ====================

@api_router.get("/")
async def root():
    return {
        "message": "Placement AI Backend API",
        "version": "1.0.0",
        "endpoints": {
            "students": "/api/students",
            "jobs": "/api/jobs",
            "applications": "/api/applications",
            "tests": "/api/tests",
            "interview_questions": "/api/interview-questions",
            "ai_matching": "/api/ai/job-match",
            "analytics": "/api/analytics"
        }
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
