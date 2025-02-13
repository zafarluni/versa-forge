import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Detect if running inside a Docker container
RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"

# Set the database host
DATABASE_HOST = "db" if RUNNING_IN_DOCKER else "localhost"
DATABASE_USER = os.getenv("POSTGRES_USER", "versa_forge_user")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD", "strongpassword")
DATABASE_NAME = os.getenv("POSTGRES_DB", "versa_forge_db")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")

DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
