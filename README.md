# UniOS — AI University Operating System

> An AI-powered university assistant that combines Retrieval-Augmented Generation (RAG), intelligent agents, course-aware retrieval, academic task management, study planning, persistent memory, and conversational AI into one unified platform.

UniOS is designed as a university-focused AI system that helps students interact with academic material, manage assignments, quizzes and labs, track deadlines, and create personalized study plans through a conversational interface.

---

## 🚀 Features

### 🤖 AI University Assistant

Interact with UniOS using natural language instead of navigating through multiple academic tools.

Examples:

- "What is TCP?"
- "Explain this concept from my CN lectures."
- "Show my quizzes."
- "What is my next deadline?"
- "Add my OS quiz tomorrow."
- "I have 2 hours today. What should I study?"

### 📚 Course-Aware RAG

UniOS uses Retrieval-Augmented Generation to answer questions from university lecture material.

The RAG pipeline includes:

```text
Lecture Files
     ↓
Document Ingestion
     ↓
Text Chunking
     ↓
HuggingFace Embeddings
     ↓
Chroma Vector Store
     ↓
Metadata-Aware Retrieval
     ↓
Question Processing
     ↓
LLM
     ↓
Grounded Answer + Sources
```

### 🧠 LangGraph Agent Architecture

UniOS uses LangGraph to orchestrate different parts of the university assistant.

```text
User Query
    ↓
Query Analysis
    ↓
Hybrid Router
    ├── RAG
    │    └── Retrieve → Generate Answer
    │
    └── Tools
         ├── Assignments
         ├── Quizzes
         ├── Labs
         ├── Deadlines
         ├── Workload
         └── Study Planner
```

### 📝 Academic Task Management

UniOS can manage:

- Assignments
- Quizzes
- Labs
- Due dates
- Pending work
- Completed tasks
- Course-specific tasks

Natural-language examples:

```text
Add my CN quiz tomorrow

Add my OS lab on September 30

Show my quizzes

Show my labs

What is my next deadline?
```

### 📅 Deadline Management

The system provides tools for academic deadline management, including:

- Next deadline
- Due today
- Due tomorrow
- Due this week
- Overdue tasks
- Next quiz
- Next lab

### 📖 Study Planner

UniOS can create study plans based on the student's available time.

Example:

```text
I have 2 hours today.
```

The system can generate a structured study plan based on pending academic work.

It also supports tracking the current study task and completing it through conversational interaction.

### 💾 Persistent Memory

UniOS maintains conversational and task-related state using persistent storage.

The system supports:

- Conversation memory
- RAG interaction history
- Tool interaction history
- Current study task
- Persistent graph state

---

## 🏗️ System Architecture

```text
                         ┌──────────────────┐
                         │   React + Vite   │
                         │    Frontend      │
                         └────────┬─────────┘
                                  │
                                  │ HTTP
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │     Backend      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    LangGraph     │
                         │  Orchestration   │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             ┌─────────────┐             ┌─────────────┐
             │     RAG     │             │    Tools    │
             └──────┬──────┘             └──────┬──────┘
                    │                           │
                    ▼                           ▼
             ┌─────────────┐             ┌─────────────┐
             │   Chroma    │             │   SQLite    │
             │ Vector DB   │             │ Academic DB │
             └──────┬──────┘             └─────────────┘
                    │
                    ▼
             ┌─────────────┐
             │ HuggingFace │
             │ Embeddings  │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │  TinyLlama  │
             │     LLM     │
             └─────────────┘
```

---

## 🛠️ Tech Stack

### Backend

- Python
- FastAPI
- LangChain
- LangGraph
- Chroma
- HuggingFace
- Transformers
- TinyLlama
- Sentence Transformers
- SQLite

### Frontend

- React
- Vite
- JavaScript
- CSS

### AI / ML

- Retrieval-Augmented Generation (RAG)
- HuggingFace Embeddings
- Sentence Transformers
- TinyLlama
- Metadata-aware retrieval
- Agent-based routing

### Document Processing

- PDF
- PowerPoint
- DOCX

---

## 📂 Project Structure

```text
UniOS/
│
├── backend/
│   └── app/
│       ├── graph/
│       ├── tools/
│       ├── agent.py
│       ├── rag.py
│       ├── retriever.py
│       ├── llm.py
│       ├── embeddings.py
│       ├── main.py
│       └── ...
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── data/
│   └── lectures/
│       ├── OS/
│       ├── OOP/
│       ├── DAA/
│       └── web and ai/
│
├── requirements.txt
├── .python-version
└── .gitignore
```

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/zubairkhan-ai/UniOS.git
cd UniOS
```

### 2. Backend Setup

Create and activate a Python virtual environment.

#### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the FastAPI backend:

```powershell
uvicorn backend.app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

### 3. Frontend Setup

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will be available through the Vite development URL shown in the terminal.

---

## 📚 Lecture Material

Lecture material is organized by course:

```text
data/
└── lectures/
    ├── OS/
    ├── OOP/
    ├── DAA/
    └── web and ai/
```

The ingestion pipeline processes supported academic documents and creates the retrieval data used by the RAG system.

---

## 🔍 RAG Pipeline

```text
PDF / PPTX / DOCX
       ↓
Document Loader
       ↓
Text Extraction
       ↓
Recursive Character Text Splitter
       ↓
Document Metadata
       ↓
HuggingFace Embeddings
       ↓
Chroma Vector Store
       ↓
Metadata-Aware Retriever
       ↓
Question Rewriter
       ↓
Question Router
       ↓
Answer Extraction / LLM
       ↓
Grounded Response
```

---

## 🧩 Academic Tools

UniOS includes tool-based workflows for:

```text
Assignments
Quizzes
Labs
Deadlines
Workload
Study Planning
Course Management
```

The conversational router determines whether a user request should be handled by an academic tool or the RAG pipeline.

---

## 🎯 Example Queries

### Academic Questions

```text
What is TCP?

Explain propositional logic.

What is gradient descent?
```

### Course Context

```text
Explain this topic from my CN lectures.

What does the DAA lecture say about this concept?
```

### Task Management

```text
Show my assignments.

Show my quizzes.

Show my labs.

Add my CN quiz tomorrow.

Add my OS lab on September 30.
```

### Planning

```text
I have 2 hours today.

What should I study?

Make me a study plan.

I finished this.
```

---

## 🔐 Configuration

Environment-specific configuration should be stored in `.env` files and should not be committed to GitHub.

Never commit API keys, tokens, passwords, or other secrets.

---

## 🚧 Current Development Status

UniOS currently includes:

- AI conversational assistant
- RAG pipeline
- Course-aware retrieval
- HuggingFace embeddings
- Chroma vector database
- TinyLlama integration
- LangGraph orchestration
- Academic task management
- Assignment management
- Quiz management
- Lab management
- Deadline management
- Study planner
- Persistent memory
- FastAPI backend
- React/Vite frontend

---

## 🔮 Future Improvements

Planned areas for future development include:

- Production-grade database infrastructure
- Scalable vector storage
- Authentication and user accounts
- Multi-user university support
- More advanced AI models
- Personalized learning analytics
- Calendar integration
- Notifications and reminders
- Advanced academic dashboards
- Cloud deployment
- Improved agent/tool orchestration

---

## 👨‍💻 Project

**UniOS — AI University Operating System**

Built as an AI-powered academic assistant combining modern LLM, RAG, agent, and web application technologies.

---

## 📄 License

This project is currently under development.
