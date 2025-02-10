# versa-forge
VersaForge – A modular, highly configurable platform for creating and managing custom GPT agents with multi-LLM support, RAG integration, and RESTful APIs.

versa-forge/
│── app/
│   ├── api/
│   │   ├── routes/          # ✅ API Endpoints
│   │   │   ├── agents.py
│   │   │   ├── files.py
│   │   │   ├── chat.py
│   │   │   ├── __init__.py
│   │   ├── dependencies.py  # ✅ Shared dependencies (DB, auth, etc.)
│   │   ├── __init__.py
│   ├── core/
│   │   ├── config.py        # ✅ Moved settings.py here (renamed)
│   │   ├── security.py
│   │   ├── __init__.py
│   ├── db/
│   │   ├── models/          # ✅ Database Models (SQLAlchemy, etc.)
│   │   │   ├── database_models.py
│   │   │   ├── __init__.py
│   │   ├── schemas/         # ✅ Pydantic Schemas
|   |   ├── postgresql
|   |   |   ├── create_db.sql
│   │   │   ├── postgresql_schema.sql
│   │   ├── migrations/      # ✅ Database Migrations (Alembic)
│   │   │   ├── versions/
│   │   │   ├── env.py
│   │   │   ├── script.py.mako
│   │   ├── database.py      # ✅ Database connection
│   │   ├── __init__.py
│   ├── services/            # ✅ Business logic (LLM, agents, etc.)
│   │   ├── agent_service.py
│   │   ├── file_service.py
│   │   ├── chat_service.py
│   │   ├── __init__.py
│   ├── llm/                 # ✅ Moved LLM-related configs and logic here
│   │   ├── llm_config.py
│   │   ├── llm.py
│   │   ├── vector_store.py
│   │   ├── __init__.py
│   ├── utils/               # ✅ Helper functions (if needed)
│   │   ├── __init__.py
│   ├── scripts/             # ✅ Automation scripts (NEW)
│   │   ├── db_seed.py       # - Script to seed initial database values
│   │   ├── backup.py        # - Backup and restore database
│   │   ├── cleanup.py       # - Cleanup old logs or temporary files
│   │   ├── __init__.py
│   ├── notebooks/           # ✅ Jupyter notebooks for R&D (NEW)
│   │   ├── llm_experiments.ipynb  # - Experiment with LLM models
│   │   ├── api_testing.ipynb      # - Test API responses
│   │   ├── db_queries.ipynb       # - Explore database queries
│   │   ├── vector_store_tests.ipynb  # - Test embeddings & retrieval
│   ├── main.py              # ✅ FastAPI entry point
│
│── tests/                   # ✅ Unit & integration tests
│   ├── test_agents.py
│   ├── test_files.py
│   ├── test_chat.py
│   ├── __init__.py
│
│── .env                     # ✅ Environment variables (DB, API keys, etc.)
│── pyproject.toml           # ✅ `uv` dependency management (replaces requirements.txt)
│── uv.lock                  # ✅ Lock file for dependencies
│── alembic.ini              # ✅ Alembic migration config
│── docker-compose.yml       # ✅ Docker setup
│── Dockerfile               # ✅ Containerization
│── README.md                # ✅ Documentation
