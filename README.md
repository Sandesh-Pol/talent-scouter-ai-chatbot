# 🚀 TalentScouter AI: Intelligent AI Hiring Assistant

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.1-green?style=for-the-badge&logo=django)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?style=for-the-badge&logo=typescript)
![Groq](https://img.shields.io/badge/Groq-Cloud-orange?style=for-the-badge)
![LLM](https://img.shields.io/badge/LLM-Llama_3.3-green?style=for-the-badge)

**TalentScouter AI** is a production-grade AI recruitment platform designed to automate the complete candidate screening process. By combining a modern **React + TypeScript** frontend with a powerful **Django REST Framework** backend and **State-Aware LLM Engine**, it conducts natural conversations, performs adaptive technical assessments, and generates professional PDF interview reports.

---

### 📺 Project Demo
Check out the Talent Scouter AI in action:

https://github.com/user-attachments/assets/f69e1c16-e910-4086-85ae-e5dc16fae4fd





## 🌟 Key Features

* **Intelligent Phase Management**: Three-stage interview flow (Profile Intake → Technical Screening → Completion) managed by a robust State Machine.
* **Real-Time Conversation**: Natural language chat interface powered by Groq's Llama 3.3-70B for human-like interactions.
* **Adaptive MCQ Screening**: Generates 5 skill-specific Multiple Choice Questions per technology based on candidate's experience level.
* **Subjective Deep-Dive**: Conducts technical interviews with 3 open-ended questions tailored to the candidate's tech stack and seniority.
* **5-Star Skill Ratings**: Automated skill assessment combining MCQ scores and subjective answer evaluations with detailed feedback.
* **Live Candidate Dashboard**: Real-time glassmorphism sidebar displaying candidate profile, tech stack, and skill ratings as data is extracted.
* **Professional PDF Reports**: One-click download of comprehensive interview reports with skill matrices and performance analysis.
* **Session Persistence**: Automatic session restoration on page refresh with localStorage integration.

---

## 🏗️ Technical Architecture

### **The Stack**

#### Frontend
* **Framework**: React 18 with TypeScript
* **Build Tool**: Vite for fast development and optimized builds
* **UI Library**: shadcn/ui components with Radix UI primitives
* **Styling**: Tailwind CSS with custom glassmorphism effects
* **Animations**: Framer Motion for smooth transitions
* **State Management**: Custom React hooks with localStorage persistence
* **Routing**: React Router v6

#### Backend
* **Framework**: Django 5.1 + Django REST Framework
* **Database**: SQLite (development) with UUID-based session IDs
* **LLM Engine**: Groq Cloud API (Llama 3.3-70B-Versatile)
* **PDF Generation**: ReportLab with custom styling
* **Rate Limiting**: Django REST Framework throttling
* **Sentiment Analysis**: Real-time candidate sentiment tracking

### **Architectural Decisions**

1. **State Machine Design**: Implemented a phase-based state machine (`onboarding` → `information_gathering` → `technical_screening` → `closing`) to maintain interview context and prevent phase confusion.

2. **Dual-State Synchronization**: Frontend maintains UI flow state (`chat` → `mcq` → `subjective` → `complete`) synchronized with backend phase state via localStorage and API polling.

3. **Context Optimization**: Uses a conversation buffer strategy with the last N messages + extracted profile data to reduce token usage while maintaining context quality.

4. **Separation of Concerns**: 
   - `prompt_orchestrator.py`: Handles all LLM interactions and prompt engineering
   - `state_machine.py`: Manages phase transitions and interview flow
   - `mcq_service.py`: Generates and evaluates technical questions
   - `pdf_service.py`: Creates formatted interview reports

5. **Error Resilience**: Implements graceful degradation with fallback responses, rate limit handling, and session restoration on network failures.

---

## 🧠 Prompt Engineering Strategy

### **Multi-Tier Prompting Architecture**

1. **Information Extraction Prompt**
   - High-precision JSON extraction from conversational text
   - Validates and structures candidate data (name, email, phone, location, experience, tech stack)
   - Handles partial information and updates existing profiles

2. **Recruiter Persona System Prompt**
   - Professional yet friendly tone
   - Contextually aware of current interview phase
   - Focuses on gathering missing information without being repetitive

3. **MCQ Generation Prompt**
   - Skill-specific questions with difficulty levels (easy/medium/hard)
   - Experience-level adaptation (junior/mid/senior)
   - Includes explanations for each correct answer

4. **Subjective Question Generator**
   - Creates open-ended technical questions
   - Focuses on problem-solving and architectural thinking
   - Tailored to candidate's tech stack and experience

5. **Answer Evaluation Prompt**
   - Scores subjective answers on a 0-1 scale
   - Provides detailed feedback with strengths and weaknesses
   - Generates improvement suggestions

---

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.9+
* Node.js 18+
* npm or bun

### Backend Setup

1. **Navigate to Backend Directory**
   ```bash
   cd backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the backend directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   DJANGO_SECRET_KEY=your_secret_key_here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start Backend Server**
   ```bash
   python manage.py runserver
   ```
   Backend will run on `http://localhost:8000`

### Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   # or
   bun install
   ```

3. **Environment Configuration**
   Create a `.env` file in the frontend directory:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

4. **Start Development Server**
   ```bash
   npm run dev
   # or
   bun run dev
   ```
   Frontend will run on `http://localhost:5173` (or the next available port)

---

## 📁 Project Structure

```
talent-scouter-ai/
├── backend/
│   ├── config/              # Django settings and configuration
│   ├── talent_scout/        # Main application
│   │   ├── models.py        # Database models (CandidateSession, ChatMessage)
│   │   ├── views.py         # REST API endpoints
│   │   ├── views_mcq.py     # MCQ and assessment endpoints
│   │   ├── serializers.py   # DRF serializers
│   │   ├── services/        # Business logic layer
│   │   │   ├── state_machine.py
│   │   │   ├── prompt_orchestrator.py
│   │   │   ├── groq_service.py
│   │   │   ├── mcq_service.py
│   │   │   ├── pdf_service.py
│   │   │   └── sentiment_service.py
│   │   └── utils/           # Utility functions
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MCQPhase.tsx
│   │   │   ├── ObjectivePhase.tsx
│   │   │   ├── CandidateSidebar.tsx
│   │   │   └── SkillRatings.tsx
│   │   ├── hooks/           # Custom React hooks
│   │   │   └── useInterviewSession.ts
│   │   ├── services/        # API client
│   │   │   └── api.ts
│   │   ├── pages/           # Page components
│   │   │   └── Index.tsx
│   │   └── types/           # TypeScript types
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## 🎯 API Endpoints

### Session Management
- `POST /api/sessions/start/` - Create new interview session
- `GET /api/sessions/{id}/status/` - Get session status and data
- `GET /api/sessions/` - List all sessions

### Chat
- `POST /api/chat/` - Send message and get AI response

### MCQ Assessment
- `POST /api/sessions/{id}/generate-mcqs/` - Generate MCQ questions
- `POST /api/sessions/{id}/submit-mcq/` - Submit MCQ answer

### Subjective Assessment
- `POST /api/sessions/{id}/generate-objectives/` - Generate subjective questions
- `POST /api/sessions/{id}/submit-objective/` - Submit subjective answer

### Reporting
- `POST /api/sessions/{id}/calculate-ratings/` - Calculate final skill ratings
- `GET /api/sessions/{id}/download-report/` - Download PDF report

---

## 🔮 Future Enhancements

- [ ] Multi-language interview support
- [ ] Video interview integration
- [ ] Advanced analytics dashboard for recruiters
- [ ] Custom question bank management
- [ ] Integration with ATS systems
- [ ] Email notification system
- [ ] Collaborative interview features (multiple interviewers)
- [ ] Real-time interviewer notes and scoring
- [ ] PostgreSQL migration for production
- [ ] Docker containerization
- [ ] CI/CD pipeline setup

---

## 📄 License

This project is licensed under the MIT License.

---
