INSERT INTO users (username, email, password_hash) VALUES
('admin', 'admin@example.com', 'pass'),
('zafarluni', 'zafarluni@example.com', 'pass')
ON CONFLICT (username) DO NOTHING;

-- INSERT INTO agents (name, description, is_public, owner_id) VALUES
-- ('Agent One', 'First AI agent', TRUE, 1),
-- ('Agent Two', 'Second AI agent', FALSE, 2)
-- ON CONFLICT (name) DO NOTHING;
