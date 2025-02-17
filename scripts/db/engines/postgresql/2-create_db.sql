-- Ensure UTF-8 encoding
SET client_encoding = 'UTF8';

-- ========================
-- Users Table
-- ========================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'), -- Basic email validation
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);


-- ========================
-- Groups Table (for class-based and role-based access)
-- ========================
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,  -- e.g., "Class 9", "Teachers", "Admin Staff"
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient lookup
CREATE INDEX IF NOT EXISTS idx_groups_name ON groups(name);


-- ========================
-- User-Groups Junction Table
-- ========================
CREATE TABLE IF NOT EXISTS user_groups (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, group_id)
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_user_groups_user_id ON user_groups(user_id);
CREATE INDEX IF NOT EXISTS idx_user_groups_group_id ON user_groups(group_id);


-- ========================
-- Categories Table
-- ========================
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);


-- ========================
-- Agents Table
-- ========================
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    prompt TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient querying
CREATE INDEX IF NOT EXISTS idx_agents_owner_id ON agents(owner_id);


-- ========================
-- Agent-Categories Junction Table
-- ========================
CREATE TABLE IF NOT EXISTS agent_categories (
    agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (agent_id, category_id)
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_agent_categories_agent_id ON agent_categories(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_categories_category_id ON agent_categories(category_id);


-- ========================
-- Agent-Groups Junction Table (to control visibility)
-- ========================
CREATE TABLE IF NOT EXISTS agent_groups (
    agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    PRIMARY KEY (agent_id, group_id)
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_agent_groups_agent_id ON agent_groups(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_groups_group_id ON agent_groups(group_id);


-- ========================
-- Agent Files Table
-- ========================
CREATE TABLE IF NOT EXISTS agent_files (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient querying
CREATE INDEX IF NOT EXISTS idx_agent_files_agent_id ON agent_files(agent_id);


