# Setup and Installation Guide: Review Conflict Resolver

## 1. Prerequisites

Ensure your host machine has the following tools installed:
- **Python**: Version 3.10+ (Verified with Python 3.13)
- **Node.js**: Version 18+ (Verified with Node v24 LTS)
- **Git**: Version 2.40+
- **Docker & Docker Compose** (Optional, for containerized PostgreSQL + pgvector + Redis)

---

## 2. Quickstart: Local Environment Setup

### 2.1 Backend Setup
1. Open PowerShell / Bash in the project root:
   ```bash
   cd c:\Review_Conflict_Resolver_AI_Project
   ```
2. Activate the virtual environment:
   - Windows PowerShell:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Linux / macOS:
     ```bash
     source venv/bin/activate
     ```
3. Install backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Configure environment variables:
   Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
   Add your Google Gemini API key or OpenAI API key in `.env`:
   ```ini
   GEMINI_API_KEY=your_actual_key_here
   ```

### 2.2 Database Initialization
The application supports two database modes:
- **PostgreSQL with pgvector (Recommended)**: Run via Docker:
  ```bash
  docker compose up -d postgres redis
  ```
- **SQLite Local Mode (Rapid Development)**:
  If running without Docker, the application automatically initializes a local SQLite database for fast local iteration.

Initialize tables and seed curated laptop datasets:
```bash
python -m backend.scripts.init_db
```

### 2.3 Starting the Backend Server
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be accessible at: `http://localhost:8000/docs`

---

## 3. Frontend Setup

1. Open a new terminal in the frontend directory:
   ```bash
   cd c:\Review_Conflict_Resolver_AI_Project\frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Vite React development server:
   ```bash
   npm run dev
   ```
4. Access the Dashboard in your browser: `http://localhost:5173`

---

## 4. Verification and Health Checks

To verify all components are operating correctly:
```bash
pytest backend/tests/ -v
```
Or run the built-in system verification check:
```bash
python -m backend.scripts.verify_system
```
