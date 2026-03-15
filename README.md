<div align="center">

<br/>

```
███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗     █████╗ ██╗
████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝    ██╔══██╗██║
██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗    ███████║██║
██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║    ██╔══██║██║
██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║    ██║  ██║██║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ╚═╝  ╚═╝╚═╝
```

### A Claude.ai-inspired multimodal AI assistant platform

*Stream conversations • Search the web • Analyze documents • Generate images • Speak & listen*

<br/>

[![Next.js](https://img.shields.io/badge/Next.js_16-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![Groq](https://img.shields.io/badge/Groq_LLaMA_3.3_70B-F55036?style=for-the-badge&logo=meta&logoColor=white)](https://groq.com/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](http://makeapullrequest.com)
[![HuggingFace](https://img.shields.io/badge/Backend-HuggingFace_Spaces-FF9D00?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/)
[![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)

</div>

---

## 🧠 What is NEXUS AI?

**NEXUS AI** is a production-grade, full-stack multimodal AI assistant platform built from scratch — inspired by Claude.ai. It combines a **Next.js 16** frontend with a **FastAPI** backend to deliver a seamless, intelligent chat experience with persistent memory, voice interaction, document analysis, and real-time web search.

> Built by [@kumardhruv88](https://github.com/kumardhruv88) — National Winner, Smart India Hackathon 2025

---

## ✨ Core Features

| Feature | Description | Stack |
|--------|-------------|-------|
| 💬 **Streaming Chat** | Real-time token streaming with Groq's LLaMA 3.3 70B | Groq, SSE |
| 🌐 **Web Search** | Live internet search injected into context | Tavily API |
| 📄 **Document Q&A** | Upload PDFs, DOCX, XLSX — ask anything about them | PyPDF2, python-docx |
| 🖼️ **Image Generation** | AI-powered image creation from text prompts | Custom pipeline |
| 🎙️ **Voice Interaction** | Speak to the AI, hear it respond | Vapi AI + ElevenLabs |
| 🧵 **Thread Management** | Persistent conversation history with full context | Supabase PostgreSQL |
| 🔐 **Auth** | Secure authentication & user management | Clerk |
| 🧠 **Memory** | Cross-session memory for personalized responses | Vector Store |
| 📦 **Artifacts** | Generate and display code, markdown, HTML inline | Custom renderer |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NEXUS AI PLATFORM                        │
│                                                                  │
│  ┌──────────────────────────┐    ┌──────────────────────────┐   │
│  │      FRONTEND            │    │       BACKEND            │   │
│  │   Next.js 16 + TS        │◄──►│    FastAPI + Python      │   │
│  │   Deployed on Vercel     │    │   Deployed on HF Spaces  │   │
│  │                          │    │                          │   │
│  │  ┌────────────────────┐  │    │  ┌────────────────────┐  │   │
│  │  │   App Router       │  │    │  │   API Routes       │  │   │
│  │  │   Components       │  │    │  │   /chat  /threads  │  │   │
│  │  │   Zustand Store    │  │    │  │   /docs  /images   │  │   │
│  │  │   TailwindCSS      │  │    │  │   /memories        │  │   │
│  │  └────────────────────┘  │    │  └────────────────────┘  │   │
│  └──────────────────────────┘    └──────────────────────────┘   │
│              │                              │                    │
│              ▼                              ▼                    │
│  ┌───────────────────┐        ┌─────────────────────────────┐   │
│  │   Auth Layer      │        │      AI Services            │   │
│  │   Clerk           │        │  ┌─────────┐ ┌──────────┐   │   │
│  └───────────────────┘        │  │  Groq   │ │  Tavily  │   │   │
│                               │  │LLaMA 3.3│ │  Search  │   │   │
│  ┌───────────────────┐        │  └─────────┘ └──────────┘   │   │
│  │   Voice Layer     │        │  ┌─────────┐ ┌──────────┐   │   │
│  │   Vapi + 11Labs   │        │  │ElevenLab│ │  Vapi AI │   │   │
│  └───────────────────┘        │  └─────────┘ └──────────┘   │   │
│                               └─────────────────────────────┘   │
│                                            │                     │
│                               ┌────────────▼──────────────┐     │
│                               │      Supabase              │     │
│                               │  PostgreSQL + Vector Store │     │
│                               │  Threads, Messages, Memory │     │
│                               └───────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
nexus-ai/
├── 📂 frontend/                    # Next.js 16 application
│   ├── 📂 app/                     # App Router pages & layouts
│   │   ├── (auth)/                 # Clerk auth routes
│   │   ├── chat/[threadId]/        # Dynamic chat pages
│   │   └── api/                    # Next.js API routes
│   ├── 📂 components/              # Reusable React components
│   │   ├── chat/                   # Chat UI components
│   │   ├── sidebar/                # Thread sidebar
│   │   └── artifacts/              # Artifact renderer
│   ├── 📂 lib/                     # Utilities & hooks
│   ├── 📂 public/                  # Static assets
│   └── .env.local                  # Frontend env vars
│
├── 📂 backend/                     # FastAPI Python application
│   ├── 📂 api/                     # Route handlers
│   │   ├── chat.py                 # Streaming chat endpoint
│   │   ├── threads.py              # Thread CRUD
│   │   ├── documents.py            # File upload & parsing
│   │   ├── images.py               # Image generation
│   │   ├── memories.py             # Memory management
│   │   └── index.py                # App entry point
│   ├── 📂 services/                # Business logic
│   │   ├── db_service.py           # Supabase operations
│   │   ├── search_service.py       # Tavily web search
│   │   ├── document_service.py     # File parsing
│   │   ├── memory_service.py       # Vector memory
│   │   └── vector_store.py         # Embeddings store
│   ├── Dockerfile                  # HuggingFace deployment
│   └── requirements.txt            # Python dependencies
│
├── .env.example                    # Environment template
├── .gitignore
└── README.md
```

---

## 🚀 Tech Stack

### Frontend
| Technology | Purpose | Version |
|-----------|---------|---------|
| **Next.js** | React framework with App Router | 16 |
| **TypeScript** | Type-safe development | 5.x |
| **Tailwind CSS** | Utility-first styling | 4.x |
| **Framer Motion** | Smooth animations | Latest |
| **Zustand** | Lightweight state management | Latest |
| **Clerk** | Authentication & user management | Latest |

### Backend
| Technology | Purpose | Version |
|-----------|---------|---------|
| **FastAPI** | High-performance Python API | 0.111.0 |
| **Uvicorn** | ASGI server | 0.29.0 |
| **Supabase** | PostgreSQL + Auth + Storage | 2.7.4 |
| **Sentence Transformers** | Vector embeddings | 2.7.0 |
| **Python-dotenv** | Environment management | 1.0.0 |

### AI & APIs
| Service | Purpose |
|---------|---------|
| **Groq (LLaMA 3.3 70B)** | Ultra-fast inference engine |
| **Tavily** | Real-time web search API |
| **ElevenLabs** | Neural text-to-speech |
| **Vapi AI** | Voice AI infrastructure |

---

## ⚙️ Local Development Setup

### Prerequisites
- Node.js v18+
- Python 3.11+
- A Supabase project
- API keys for Groq, Tavily, ElevenLabs, Vapi, Clerk

### 1. Clone the repository
```bash
git clone https://github.com/kumardhruv88/multimodel.git
cd multimodel
```

### 2. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
# Fill in your keys in .env.local
npm run dev
```
Frontend runs at `http://localhost:3000`

### 3. Backend Setup
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
# Create .env with your keys (see .env.example)
uvicorn api.index:app --reload --port 8000
```
Backend runs at `http://localhost:8000`

---

## 🌍 Deployment

### Backend → HuggingFace Spaces (Docker)
```bash
cd backend
git init
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
git add .
git commit -m "Deploy backend"
git push origin main --force
```
Set these secrets in HF Space → Settings → Variables and secrets:
- `GROQ_API_KEY`
- `TAVILY_API_KEY`
- `ELEVEN_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

### Frontend → Vercel
1. Import repo from GitHub at [vercel.com](https://vercel.com)
2. Set **Root Directory** to `frontend`
3. Add all env vars from `.env.local`
4. Deploy 🚀

---

## 🔑 Environment Variables

```env
# Frontend (.env.local)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
NEXT_PUBLIC_VAPI_PUBLIC_KEY=...
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_API_URL=https://your-backend.hf.space

# Backend (.env)
GROQ_API_KEY=gsk_...
TAVILY_API_KEY=tvly-...
ELEVEN_API_KEY=sk_...
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit PRs.

```bash
# Fork → Clone → Create branch → Make changes → PR
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

---

## 📜 License

MIT License © 2026 [Dhruv Kumar](https://github.com/kumardhruv88)

---

<div align="center">

Built with ❤️ by **Dhruv Kumar** | National Winner SIH 2025 | GSoC 2026

⭐ Star this repo if you found it useful!

</div>
