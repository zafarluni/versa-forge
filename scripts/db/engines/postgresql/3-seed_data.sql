-- ========================
-- Seed Users
-- ========================
INSERT INTO users (username, email, password_hash) VALUES
('admin', 'admin@example.com', 'pass'),
('zafarluni', 'zafarluni@example.com', 'pass')
ON CONFLICT (username) DO NOTHING;

-- ========================
-- Seed Agents (Optional Placeholder)
-- Uncomment if needed
-- ========================
-- INSERT INTO agents (name, description, is_public, owner_id) VALUES
-- ('Agent One', 'First AI agent', TRUE, 1),
-- ('Agent Two', 'Second AI agent', FALSE, 2)
-- ON CONFLICT (name) DO NOTHING;

-- ========================
-- Seed Categories for Educational Domains
-- ========================

-- Categories for Grades 9-10
INSERT INTO categories (name, description) 
VALUES 
('Biology - Grade 9-10', 'Biology educational resources and assistant bots for grades 9 and 10'),
('Chemistry - Grade 9-10', 'Chemistry educational resources and assistant bots for grades 9 and 10'),
('Physics - Grade 9-10', 'Physics educational resources and assistant bots for grades 9 and 10'),
('Mathematics - Grade 9-10', 'Mathematics tutoring and learning assistants for grades 9 and 10')
ON CONFLICT (name) DO NOTHING;

-- Categories for Grades 11-12
INSERT INTO categories (name, description) 
VALUES 
('Biology - Grade 11-12', 'Biology educational resources and assistant bots for grades 11 and 12'),
('Chemistry - Grade 11-12', 'Chemistry educational resources and assistant bots for grades 11 and 12'),
('Physics - Grade 11-12', 'Physics educational resources and assistant bots for grades 11 and 12'),
('Mathematics - Grade 11-12', 'Mathematics tutoring and learning assistants for grades 11 and 12')
ON CONFLICT (name) DO NOTHING;

-- ========================
-- Seed User Groups
-- ========================

-- Class-Based Groups
INSERT INTO groups (name, description) 
VALUES 
('Class 9', 'Group for Grade 9 students'),
('Class 10', 'Group for Grade 10 students'),
('Class 11', 'Group for Grade 11 students'),
('Class 12', 'Group for Grade 12 students')
ON CONFLICT (name) DO NOTHING;

-- Role-Based Groups
INSERT INTO groups (name, description) 
VALUES 
('Teachers', 'Group for teaching staff'),
('Admin Staff', 'Group for administrative staff')
ON CONFLICT (name) DO NOTHING;

-- ========================
-- Seed User-Group Assignments
-- ========================

-- Assign users to groups
-- Admin assigned to Admin Staff group
INSERT INTO user_groups (user_id, group_id)
SELECT u.id, g.id 
FROM users u, groups g
WHERE u.username = 'admin' AND g.name = 'Admin Staff'
ON CONFLICT DO NOTHING;

-- Assign zafarluni to Class 9 group (example)
INSERT INTO user_groups (user_id, group_id)
SELECT u.id, g.id 
FROM users u, groups g
WHERE u.username = 'zafarluni' AND g.name = 'Class 9'
ON CONFLICT DO NOTHING;

-- ========================
-- Seed Agent-Groups Assignments (Optional)
-- ========================

-- Assign Category 9-10 Subject Tutors to Class 9 Group
INSERT INTO agent_groups (agent_id, group_id)
SELECT a.id, g.id 
FROM agents a, groups g
WHERE a.name = 'Agent One' AND g.name = 'Class 9'
ON CONFLICT DO NOTHING;

