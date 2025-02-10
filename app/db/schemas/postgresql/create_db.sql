-- Create a new database
CREATE DATABASE versa_forge_db;

-- Create a new user with a strong password
CREATE USER versa_forge_user WITH PASSWORD 'strongpassword';

-- Grant privileges to the user on the database
GRANT ALL PRIVILEGES ON DATABASE versa_forge_db TO versa_forge_user;

-- Set the default encoding and collation
ALTER DATABASE versa_forge_db SET client_encoding TO 'utf8';
ALTER DATABASE versa_forge_db SET timezone TO 'UTC';
