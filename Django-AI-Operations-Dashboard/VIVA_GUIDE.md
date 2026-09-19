# AI Operations Dashboard - Comprehensive Viva Guide & Manual

This document is your complete project defense (**Viva**) guide. It explains architecture, AI features, setup, testing, and how every component works.

---

## 1. Technical Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | Django 5.x + DRF | REST API, business logic, AI services |
| Database | SQLite (dev) / PostgreSQL (prod) | Relational data + JSON embeddings |
| Task Queue | Celery + Redis | Background AI processing |
| Auth | SimpleJWT + RBAC | Secure token-based login (Admin/Manager/Employee) |
| Frontend | React 19 + Vite | SPA dashboard UI |
| AI (offline) | TF-IDF embeddings + keyword classifiers | Works without API keys |
| AI (optional) | OpenAI GPT | Enhanced answers when `OPENAI_API_KEY` is set |
| Documents | pypdf, python-docx | PDF/DOCX/TXT text extraction |

---

## 2. System Architecture

```
┌─────────────────┐     JWT REST API      ┌──────────────────────────────────┐
│  React Frontend │ ◄──────────────────► │         Django Backend           │
│  (port 5173)    │                      │  users, tasks, tickets, docs, ai │
└─────────────────┘                      └──────────────┬───────────────────┘
                                                        │
                        ┌───────────────────────────────┼───────────────────────┐
                        │                               │                       │
                        ▼                               ▼                       ▼
                 ┌─────────────┐               ┌─────────────────┐      ┌──────────────┐
                 │   SQLite    │               │  Celery Worker  │      │    Redis     │
                 │  Database   │               │  (background)   │      │   (broker)   │
                 └─────────────┘               └─────────────────┘      └──────────────┘
```

### How AI Fits In

1. **Upload** → Document saved to `media/documents/`
2. **Celery task** → Extract text → Split chunks → Generate embeddings → Store in `DocumentChunk`
3. **RAG Chat** → User question → Vector search → Top chunks → LLM answer with sources
4. **Ticket** → Created → Celery classifies category/priority/department
5. **Agent** → User request → Tool selection → Execute or request human approval
6. **Logging** → Every AI call saved to `AIInteractionLog`

---

## 3. AI Features (All Implemented)

### 3.1 Document Upload & Processing
- **Supported formats:** PDF, DOCX, TXT only
- **Pipeline:** Upload → `process_document_task` (Celery) → extract → chunk (500 chars, 80 overlap) → TF-IDF embed → store
- **Models:** `Document` (extended), `DocumentChunk` (vectors as JSON)
- **API:** `POST /api/documents/`, `POST /api/ai/documents/{id}/reprocess/`, `GET /api/ai/documents/{id}/chunks/`
- **UI:** `/documents` — shows processing status badges (Pending/Processing/Indexed/Failed)

### 3.2 RAG Chatbot
- Answers **only** from uploaded documents (no hallucination from general knowledge in local mode)
- Returns **source references:** document title, chunk index, excerpt, relevance score
- **API:** `POST /api/ai/chat/`, `GET /api/ai/chat/sessions/`
- **UI:** `/ai-chat`

### 3.3 AI Ticket Classification
- Predicts: **category** (Hardware/Software/Network/Access/AI-ML), **priority**, **department**
- Runs automatically on ticket creation via Celery
- **API:** `POST /api/ai/classify-ticket/`
- **UI:** `/tickets` — AI badges on each ticket card

### 3.4 AI Summary
- Generates document summaries (extractive offline, GPT if API key set)
- Auto-runs during document processing; can be triggered manually
- **API:** `POST /api/ai/summarize/` with `document_id` or `text`

### 3.5 AI Report Generator
- Aggregates tasks, tickets, documents, AI logs for the past week
- Generated asynchronously via Celery
- **API:** `POST /api/ai/reports/`, `GET /api/ai/reports/`
- **UI:** `/ai-reports` (Admin/Manager only)

### 3.6 AI Agent
- Receives natural-language requests
- **Tools:** search_documents, classify_ticket, summarize_document, generate_report, assign_ticket*, send_email*
- *Requires human approval before execution
- **API:** `POST /api/ai/agent/runs/run/`, `POST /api/ai/agent/runs/{id}/approve/`
- **UI:** `/ai-agent`

### 3.7 Background Tasks (Celery + Redis)
| Task | Trigger | Purpose |
|------|---------|---------|
| `process_document_task` | Document upload | Extract, chunk, embed |
| `classify_ticket_task` | Ticket creation | AI classification |
| `generate_report_task` | Report request | Weekly report |
| `send_email_task` | Agent approval | Email delivery |
| `cleanup_old_notifications` | Beat (daily) | Housekeeping |
| `check_due_tasks_summary` | Beat (hourly) | Deadline alerts |

### 3.8 AI Interaction Logging
- Every AI operation logged to `AIInteractionLog` table
- Fields: type, input, output, model, tokens, duration, success
- **API:** `GET /api/ai/interactions/`
- Visible in Django Admin under **AI Operations**

---

## 4. Authentication (JWT + RBAC)

| Role | Permissions |
|------|------------|
| **ADMIN** | Full access — users, departments, AI reports, all data |
| **MANAGER** | Tasks, tickets, documents, AI reports, activity logs |
| **EMPLOYEE** | Own tasks/tickets, documents, AI chat, AI agent |

**Seeded credentials:**
- Admin: `admin` / `admin123`
- Manager: `manager` / `manager123`
- Employee: `employee` / `employee123`

**Auth flow:**
1. `POST /api/auth/token/` → access + refresh tokens
2. Frontend stores tokens in localStorage
3. Axios interceptor attaches `Authorization: Bearer <token>`
4. On 401 → auto-refresh → retry request

---

## 5. Step-by-Step Setup (4 Terminals)

### Terminal 1 — Backend
```powershell
cd D:\GitHub\Django-AI-Operations-Dashboard\backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python seed.py
python manage.py runserver 8000
```

### Terminal 2 — Redis (required for Celery)
```powershell
# Option A: Docker
docker run -d -p 6379:6379 redis:7-alpine

# Option B: docker-compose from project root
cd D:\GitHub\Django-AI-Operations-Dashboard
docker-compose up redis -d
```

### Terminal 3 — Celery Worker
```powershell
cd D:\GitHub\Django-AI-Operations-Dashboard\backend
venv\Scripts\Activate.ps1
celery -A config worker --loglevel=info -P solo
# Use -P eventlet on Windows if solo fails
```

### Terminal 4 — Frontend
```powershell
cd D:\GitHub\Django-AI-Operations-Dashboard
npm run frontend-install
npm run dev
```

Open: **http://localhost:5173/** — Login as `admin` / `admin123`

---

## 6. How to Test Every Feature

### Test 1: Authentication
1. Go to `/login` → login as `admin` / `admin123`
2. Verify sidebar shows all menu items
3. Logout → login as `employee` / `employee123`
4. Verify `/users` and `/ai-reports` are hidden (RBAC)

### Test 2: Document Upload & Processing
1. Go to `/documents` → Upload a `.txt` file with sample content:
   ```
   Our RAG pipeline uses document chunking and TF-IDF embeddings.
   The Celery worker processes PDF, DOCX, and TXT files asynchronously.
   ```
2. Wait 5–10 seconds → status badge changes to **Indexed**
3. Verify chunk count appears on the card
4. Click sparkle icon for AI summary

**API test (Swagger):**
```
POST /api/documents/  (multipart: title, file)
GET  /api/ai/documents/{id}/chunks/
```

### Test 3: RAG Chatbot
1. Go to `/ai-chat`
2. Ask: *"What is the RAG pipeline?"*
3. Verify answer references your uploaded document
4. Check **Sources** section shows document title + chunk excerpt

**API test:**
```json
POST /api/ai/chat/
{ "question": "What is the RAG pipeline?" }
```

### Test 4: AI Ticket Classification
1. Go to `/tickets` → Create ticket:
   - Subject: *"VPN connection keeps dropping"*
   - Description: *"Remote team cannot connect to office network via VPN"*
2. Wait a few seconds → refresh page
3. Verify AI badges: Category=Network, Department=IT Support

**API test:**
```json
POST /api/ai/classify-ticket/
{ "subject": "GPU memory error", "description": "Model training fails with CUDA OOM" }
```

### Test 5: AI Report Generator
1. Login as admin/manager → `/ai-reports`
2. Click **Generate Report**
3. Wait for status **Completed** → preview and download `.md` file

### Test 6: AI Agent
1. Go to `/ai-agent`
2. Try: *"What documents do we have about RAG?"* → uses search_documents tool
3. Try: *"Assign ticket #1 to manager"* → shows **Human Approval Required**
4. Click Approve or Reject

### Test 7: AI Interaction Logs
1. Django Admin → **AI Interaction logs** — see all logged operations
2. Or API: `GET /api/ai/interactions/`

### Test 8: Celery Background Tasks
1. Upload a document WITHOUT Celery running → processes synchronously (fallback)
2. Start Celery worker → upload another doc → check worker terminal for task logs
3. Create ticket → worker logs `classify_ticket_task`

---

## 7. REST API Reference (AI Endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/chat/` | RAG chatbot question |
| GET | `/api/ai/chat/sessions/` | List chat sessions |
| POST | `/api/ai/classify-ticket/` | Classify ticket text |
| POST | `/api/ai/summarize/` | Summarize text/document |
| POST | `/api/ai/reports/` | Generate weekly report |
| GET | `/api/ai/reports/` | List reports |
| POST | `/api/ai/agent/runs/run/` | Run AI agent |
| GET | `/api/ai/agent/runs/` | List agent runs |
| POST | `/api/ai/agent/runs/{id}/approve/` | Approve/reject agent action |
| GET | `/api/ai/interactions/` | AI audit logs |
| POST | `/api/ai/documents/{id}/reprocess/` | Re-process document |
| GET | `/api/ai/documents/{id}/chunks/` | List document chunks |

Full Swagger docs: **http://localhost:8000/api/schema/swagger-ui/**

---

## 8. Code Structure (Where to Find Things)

```
backend/apps/ai/
├── models.py              # DocumentChunk, ChatSession, AIInteractionLog, AgentRun, etc.
├── views.py               # REST API endpoints
├── tasks.py               # Celery background tasks
├── serializers.py         # Request/response validation
└── services/
    ├── document_processor.py  # PDF/DOCX/TXT extraction + chunking
    ├── embeddings.py          # TF-IDF vector generation
    ├── vector_store.py        # Semantic search over chunks
    ├── rag.py                 # RAG chatbot pipeline
    ├── classifier.py          # Ticket classification
    ├── summarizer.py          # Document summaries
    ├── report_generator.py    # Weekly reports
    ├── agent.py               # AI agent + approval workflow
    └── interaction_logger.py  # Audit logging

frontend/src/pages/
├── AIChatPage.jsx         # RAG chatbot UI
├── AIAgentPage.jsx        # AI agent console
├── AIReportsPage.jsx      # Report generator
├── DocumentManagement.jsx # Upload + processing status
└── Dashboard.jsx          # Real AI activity stats
```

---

## 9. Optional: Enable OpenAI GPT

Add to `backend/.env`:
```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```
Restart Django. RAG, classification, summaries, and reports will use GPT instead of local fallback.

---

## 10. Viva Q&A — Common Questions

**Q: What is RAG?**
A: Retrieval-Augmented Generation. We retrieve relevant document chunks via vector search, then generate answers grounded in that context only.

**Q: Why TF-IDF instead of neural embeddings?**
A: Works offline without GPU/API keys — ideal for development and viva demo. Production can swap to sentence-transformers or OpenAI embeddings.

**Q: How does the AI Agent work?**
A: Keyword-based intent router selects a tool. Sensitive actions (assign ticket, send email) pause for human approval via `AgentApproval` model.

**Q: How is authentication secured?**
A: JWT with refresh token rotation, blacklist on logout, RBAC on every endpoint, CORS restricted to frontend origin.

**Q: What runs in background?**
A: Celery workers handle document processing, ticket classification, report generation, and email sending via Redis message broker.

**Q: How are AI interactions audited?**
A: Every call creates an `AIInteractionLog` record with input, output, model, duration, and success status.

---

## 11. Troubleshooting

| Problem | Solution |
|---------|----------|
| Document stuck on Pending | Start Celery worker; or click Reprocess button |
| RAG says no documents | Wait for processing_status = COMPLETED |
| 401 Unauthorized | Re-login; check token in localStorage |
| Celery connection error | Start Redis on port 6379 |
| PDF extraction empty | PDF may be scanned image — use OCR or TXT instead |
| Employee can't see AI reports | Expected — Admin/Manager only (RBAC) |

---

## 12. Default URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173/ |
| Backend API | http://localhost:8000/api/ |
| Swagger Docs | http://localhost:8000/api/schema/swagger-ui/ |
| Django Admin | http://localhost:8000/admin/ |
