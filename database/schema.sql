-- PlacePredict: AI-Powered Placement Analysis System
-- PostgreSQL Database Schema

-- Create database extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table (central authentication table)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('student', 'faculty', 'recruiter', 'admin')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Students table
CREATE TABLE students (
    student_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    department VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1 AND 4),
    cgpa DECIMAL(4,2) CHECK (cgpa >= 0 AND cgpa <= 10),
    skills JSONB DEFAULT '[]',
    resume_url VARCHAR(500),
    eligibility_status VARCHAR(50) DEFAULT 'pending' CHECK (eligibility_status IN ('pending', 'eligible', 'not_eligible')),
    placement_status VARCHAR(50) DEFAULT 'unplaced' CHECK (placement_status IN ('unplaced', 'placed', 'higher_studies', 'entrepreneurship')),
    placed_company VARCHAR(200),
    placed_role VARCHAR(200),
    package_lpa DECIMAL(10,2),
    placement_score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Faculty table
CREATE TABLE faculty (
    faculty_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    department VARCHAR(100) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Recruiters table
CREATE TABLE recruiters (
    recruiter_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company VARCHAR(200) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    industry VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recruiter_id UUID NOT NULL REFERENCES recruiters(recruiter_id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    company VARCHAR(200) NOT NULL,
    location VARCHAR(200),
    job_type VARCHAR(50) DEFAULT 'full_time' CHECK (job_type IN ('full_time', 'part_time', 'internship', 'contract')),
    experience_level VARCHAR(50) DEFAULT 'entry' CHECK (experience_level IN ('entry', 'mid', 'senior')),
    required_skills TEXT[] DEFAULT '{}',
    description TEXT,
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    posted_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deadline TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Applications table
CREATE TABLE applications (
    app_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'applied' CHECK (status IN ('applied', 'shortlisted', 'interviewed', 'hired', 'rejected')),
    applied_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, student_id)
);

-- Assessments table
CREATE TABLE assessments (
    assessment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('mock_test', 'skill_test', 'interview')),
    category VARCHAR(100) NOT NULL,
    score INTEGER NOT NULL CHECK (score >= 0),
    total_questions INTEGER NOT NULL CHECK (total_questions > 0),
    correct_answers INTEGER NOT NULL CHECK (correct_answers >= 0),
    difficulty VARCHAR(20) DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard')),
    feedback TEXT,
    recommendations TEXT[] DEFAULT '{}',
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    duration_minutes INTEGER
);

-- Skill Analysis table
CREATE TABLE skill_analysis (
    skill_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    current_demand INTEGER DEFAULT 0,
    predicted_demand INTEGER DEFAULT 0,
    growth_rate DECIMAL(5,2) DEFAULT 0,
    industry_focus TEXT[] DEFAULT '{}',
    trend VARCHAR(20) DEFAULT 'stable' CHECK (trend IN ('rising', 'falling', 'stable')),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE notifications (
    notif_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'error')),
    status VARCHAR(20) DEFAULT 'unread' CHECK (status IN ('read', 'unread')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE documents (
    doc_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('resume', 'certificate', 'portfolio')),
    file_name VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size INTEGER,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Activity Logs table
CREATE TABLE activity_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Company Placements table (for analytics)
CREATE TABLE company_placements (
    placement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES students(student_id),
    company VARCHAR(200) NOT NULL,
    role VARCHAR(200) NOT NULL,
    package_lpa DECIMAL(10,2),
    placement_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    academic_year VARCHAR(10),
    department VARCHAR(100)
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_students_department ON students(department);
CREATE INDEX idx_students_year ON students(year);
CREATE INDEX idx_students_placement_status ON students(placement_status);
CREATE INDEX idx_jobs_company ON jobs(company);
CREATE INDEX idx_jobs_active ON jobs(is_active);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_assessments_type ON assessments(type);
CREATE INDEX idx_assessments_student ON assessments(student_id);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_skill_analysis_trend ON skill_analysis(trend);
CREATE INDEX idx_activity_logs_user ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_timestamp ON activity_logs(timestamp);

-- Create triggers for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample skill data
INSERT INTO skill_analysis (skill_name, category, current_demand, predicted_demand, growth_rate, industry_focus, trend) VALUES
('Python', 'Programming', 85, 95, 11.76, ARRAY['Software', 'Data Science', 'AI/ML'], 'rising'),
('JavaScript', 'Programming', 90, 88, -2.22, ARRAY['Web Development', 'Full Stack'], 'falling'),
('React', 'Frontend', 80, 85, 6.25, ARRAY['Web Development', 'UI/UX'], 'rising'),
('Node.js', 'Backend', 75, 82, 9.33, ARRAY['Web Development', 'API'], 'rising'),
('Machine Learning', 'AI/ML', 70, 88, 25.71, ARRAY['AI/ML', 'Data Science'], 'rising'),
('Docker', 'DevOps', 65, 78, 20.00, ARRAY['DevOps', 'Cloud'], 'rising'),
('AWS', 'Cloud', 75, 85, 13.33, ARRAY['Cloud', 'DevOps'], 'rising'),
('SQL', 'Database', 85, 80, -5.88, ARRAY['Database', 'Analytics'], 'stable'),
('MongoDB', 'Database', 60, 70, 16.67, ARRAY['Database', 'NoSQL'], 'rising'),
('Java', 'Programming', 80, 75, -6.25, ARRAY['Enterprise', 'Backend'], 'falling');

-- Create sample admin user (password: admin123)
INSERT INTO users (full_name, email, password_hash, role) VALUES 
('System Admin', 'admin@placepredict.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewWfND9Pt8/Z9heG', 'admin');