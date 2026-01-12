-- Job Search Application Database Schema
-- PostgreSQL

-- User profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    linkedin VARCHAR(255),
    github VARCHAR(255),
    website VARCHAR(255),
    location VARCHAR(255),
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    board VARCHAR(100),
    ats_type VARCHAR(50),
    logo_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, board)
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) NOT NULL,
    company_id INTEGER REFERENCES companies(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    location VARCHAR(255),
    department VARCHAR(255),
    description TEXT,
    salary VARCHAR(255),
    work_type VARCHAR(50),
    url VARCHAR(1000),
    posted_date TIMESTAMP WITH TIME ZONE,
    source VARCHAR(50) NOT NULL,
    match_score DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(external_id, source)
);

-- Job applications table
CREATE TABLE IF NOT EXISTS job_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user_profiles(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'applied',
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id)
);

-- Excluded jobs table
CREATE TABLE IF NOT EXISTS excluded_jobs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user_profiles(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    excluded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(255),
    UNIQUE(user_id, job_id)
);

-- Generated documents table
CREATE TABLE IF NOT EXISTS generated_documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user_profiles(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    ai_model VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User settings table
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user_profiles(id) ON DELETE CASCADE,
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, setting_key)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_jobs_company_id ON jobs(company_id);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_match_score ON jobs(match_score DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active);
CREATE INDEX IF NOT EXISTS idx_jobs_external_id ON jobs(external_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_user_id ON job_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_status ON job_applications(status);
CREATE INDEX IF NOT EXISTS idx_excluded_jobs_user_id ON excluded_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_documents_job_id ON generated_documents(job_id);
CREATE INDEX IF NOT EXISTS idx_generated_documents_type ON generated_documents(document_type);

-- Full text search index for job descriptions
CREATE INDEX IF NOT EXISTS idx_jobs_fts ON jobs USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')));

-- Insert default user profile
INSERT INTO user_profiles (name, title, email, linkedin, github, website, location, summary)
VALUES (
    'Sudhakar Chundu',
    'Cloud AI Architect',
    'chundubabu@gmail.com',
    'https://www.linkedin.com/in/schundu',
    'https://github.com/schundu007',
    'https://www.sudhakarchundu.org',
    'United States',
    'Cloud AI Architect with 18+ years of experience in enterprise infrastructure, AI/ML platforms, and DevOps transformation. Expert in Kubernetes, GPU infrastructure, and building scalable cloud-native platforms.'
) ON CONFLICT DO NOTHING;
