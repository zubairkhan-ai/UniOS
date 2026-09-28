# UniOS — AI University Operating System

> An AI-powered university assistant that combines Retrieval-Augmented Generation (RAG), intelligent agents, course-aware retrieval, academic task management, study planning, persistent memory, and conversational AI into one unified platform.

UniOS is designed as a university-focused AI system that helps students interact with their academic material, manage assignments, quizzes and labs, track deadlines, and create personalized study plans through a conversational interface.

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

---

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


🧠 LangGraph Agent Architecture

UniOS uses LangGraph to orchestrate different parts of the university assistant.

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
📝 Academic Task Management

UniOS can manage:

Assignments
Quizzes
Labs
Due dates
Pending work
Completed tasks
Course-specific tasks

Natural-language examples:

Add my CN quiz tomorrow

Add my OS lab on September 30

Show my quizzes

Show my labs

What is my next deadline?
📅 Deadline Management

The system provides tools for academic deadline management, including:

Next deadline
Due today
Due tomorrow
Due this week
Overdue tasks
Next quiz
Next lab
📖 Study Planner

UniOS can create study plans based on the student's available time.

Example:

I have 2 hours today.

The system can generate a structured study plan based on pending academic work.

It also supports tracking the current study task and completing it through conversational interaction.

💾 Persistent Memory

UniOS maintains conversational and task-related state using persistent storage.

The system supports:

Conversation memory
RAG interaction history
Tool interaction history
Current study task
Persistent graph state
💾 Persistent Memory

UniOS maintains conversational and task-related state using persistent storage.

The system supports:

Conversation memory
RAG interaction history
Tool interaction history
Current study task
Persistent graph state

.

🚧 Current Development Status

UniOS currently includes:

AI conversational assistant
RAG pipeline
Course-aware retrieval
HuggingFace embeddings
Chroma vector database
TinyLlama integration
LangGraph orchestration
Academic task management
Assignment management
Quiz management
Lab management
Deadline management
Study planner
Persistent memory
FastAPI backend
React/Vite frontend
🔮 Future Improvements

Planned areas for future development include:

Production-grade database infrastructure
Scalable vector storage
Authentication and user accounts
Multi-user university support
More advanced AI models
Personalized learning analytics
Calendar integration
Notifications and reminders
Advanced academic dashboards
Cloud deployment
Improved agent/tool orchestration
👨‍💻 Project

UniOS — AI University Operating System

Built as an AI-powered academic assistant combining modern LLM, RAG, agent, and web application technologies.

📄 License

This project is currently under development.


---

## STEP 9 — Commit

README paste karne ke baad page ke **bottom** par jao.

Wahan:

**Commit changes**

Commit message:

```text
Add project README
