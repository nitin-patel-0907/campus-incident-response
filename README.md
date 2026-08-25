<p align="center">
  <img src="https://img.shields.io/badge/Built%20For-Agentathon%202025-blueviolet?style=for-the-badge" alt="Agentathon 2025" />
  <img src="https://img.shields.io/badge/Hackathon-First%20College%20Hackathon-FF6B6B?style=for-the-badge&logo=eventbrite&logoColor=white" alt="First College Hackathon" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/FastAPI-0.128-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/LangGraph-1.0-FF6F00?style=for-the-badge" alt="LangGraph" />
</p>

# 🚨 AI For Campus Safety — Incident Report Analysis System

> **A multi-agent AI platform that automates and streamlines campus incident management — from intake to resolution — using 5 specialized AI agents working collaboratively.**

---

## 🏆 The Hackathon Story: My Very First College Hackathon!

This project was envisioned, designed, and built for **Agentathon 2025**, which proudly marks **my very first college hackathon!** 

Faced with a high-intensity environment, a 48-hour time constraint, and the challenge of building a production-grade multi-agent workflow, I set out to solve a real-world problem: **campus safety and compliance.** Using **LangGraph** to coordinate agents and a unified **FastAPI + React** stack, I built this complete, end-to-end incident management platform. 

Participating in my first college hackathon allowed me to push the boundaries of what is possible with autonomous AI agent coordination, full-stack integration, and safety compliance, transforming a complex idea into a fully working project.

---

## 🎯 What It Does

The system automates the **full lifecycle** of campus incident management:

1. A student or staff member **submits an incident report** (via web UI, CLI, or API).
2. The AI agent swarm **processes, classifies, plans, validates, executes, and evaluates** the response — all in real-time.
3. Results are aggregated on a **beautiful React dashboard** showing real-time analytics, performance insights, and a human-in-the-loop review queue.

### Key Capabilities

* 🤖 **5 Autonomous AI Agents** working in a coordinated LangGraph pipeline.
* 🛡️ **Safety-First Architecture** with strict Title IX, FERPA, and campus policy compliance.
* 📊 **Real-time Analytics Dashboard** with interactive charts, incident distributions, and performance metrics.
* 🔍 **Spam & Gibberish Detection** using Groq LLM + a Reinforcement Learning feedback loop.
* 👥 **Human-in-the-Loop Review** queue to handle flagged or sensitive incidents safely.
* 📈 **AI vs Human Performance Comparison** with confidence scoring and quality tracking.
* 🌐 **WebSocket Support** for live incident processing status updates.

---

## 🤖 Multi-Agent Architecture

The system achieves intelligent incident processing through five specialized AI agents, coordinated by an orchestrator using a defined pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│                     INCIDENT REPORT INPUT                       │
│              (Web UI  /  CLI  /  REST API)                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   📝 PROMPT AGENT      │  ← Intake & Classification
              │   Extract structured   │
              │   data, classify type  │
              │   & severity           │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │   📋 PLANNER AGENT     │  ← Action Planning
              │   Create step-by-step  │
              │   plan, identify       │
              │   stakeholders         │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │   🔒 SAFETY & POLICY   │  ← Compliance Validation
              │   AGENT                │
              │   Title IX, FERPA,     │
              │   harmful action block │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │   ⚙️ EXECUTOR AGENT    │  ← Plan Execution
              │   Simulate/execute     │
              │   approved actions,    │
              │   resource allocation  │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │   📊 EVALUATOR AGENT   │  ← Quality Assessment
              │   Score effectiveness, │
              │   generate improvement │
              │   recommendations      │
              └────────────────────────┘
```

| Agent | Role | Key Capabilities |
| :--- | :--- | :--- |
| **📝 Prompt Agent** | Intake & Classification | Extracts structured data from raw text, classifies incident type and severity |
| **📋 Planner Agent** | Action Planning | Creates step-by-step action plans, identifies stakeholders, establishes timelines |
| **🔒 Safety & Policy Agent** | Compliance Validation | Cross-references against Title IX, FERPA, campus policies; blocks harmful actions |
| **⚙️ Executor Agent** | Plan Execution | Simulates/executes the approved plan, manages resource allocation and notifications |
| **📊 Evaluator Agent** | Quality Assessment | Scores response effectiveness (0-100), provides insights for continuous improvement |

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
| :--- | :--- |
| **Python 3.11+** | Core language |
| **FastAPI** | High-performance async REST API and file serving |
| **LangGraph** | Multi-agent workflow orchestration |
| **LangChain** | LLM integration framework |
| **OpenAI / Groq** | LLM providers for AI reasoning and spam detection |
| **Pydantic** | Data validation and serialization |
| **WebSockets** | Real-time incident processing updates |

### Frontend
| Technology | Purpose |
| :--- | :--- |
| **React 18** | UI framework |
| **TypeScript** | Type-safe development |
| **Vite** | Build tool and dev server |
| **TailwindCSS** | Utility-first styling |
| **ShadCN UI** | Radix-based premium component library |
| **Recharts** | Data visualization & analytics charts |
| **Framer Motion** | Fluid micro-animations and transitions |
| **React Query** | Data fetching and caching |

---

## 📁 Project Structure

```
AGENTATHON/
├── src/                          # Core application source code
│   ├── agents/                   # 5 AI Agent implementations
│   │   ├── base_agent.py         #   Abstract base class for all agents
│   │   ├── prompt_agent.py       #   Intake & classification agent
│   │   ├── planner_agent.py      #   Action planning agent
│   │   ├── safety_policy_agent.py#   Compliance validation agent
│   │   ├── executor_agent.py     #   Plan execution agent
│   │   └── evaluator_agent.py    #   Quality assessment agent
│   │
│   ├── app/                      # Web application layer
│   │   ├── app.py                #   Flask web server (legacy helper)
│   │   ├── cli.py                #   Command-line interface
│   │   └── orchestrator.py       #   Multi-agent workflow coordinator
│   │
│   ├── backend/                  # FastAPI backend services
│   │   ├── api/                  #   REST API endpoints
│   │   │   ├── realtime_api.py   #     Real-time incident processing API
│   │   │   ├── analytics_api.py  #     Analytics & insights API
│   │   │   └── data_simulator.py #     Demo data simulation
│   │   ├── graph/                #   LangGraph workflow definitions
│   │   │   └── incident_workflow.py
│   │   ├── llm/                  #   LLM provider clients
│   │   │   ├── multi_provider_client.py
│   │   │   └── openai_client.py
│   │   ├── nodes/                #   LangGraph node implementations
│   │   │   ├── intake_node.py
│   │   │   ├── planner_node.py
│   │   │   ├── safety_node.py
│   │   │   ├── executor_node.py
│   │   │   ├── evaluator_node.py
│   │   │   └── fraud_detection_node.py
│   │   └── services/             #   Business logic services
│   │       ├── file_authenticity_service.py
│   │       ├── human_review_service.py
│   │       └── resolution_service.py
│   │
│   └── core/                     # Core utilities & ML modules
│       ├── spam_detector.py      #   Groq-powered spam detection
│       ├── gibberish_detector.py #   Gibberish content filtering
│       ├── reinforcement_learning.py  # RL-based learning system
│       ├── confidence_index_calculator.py
│       └── incident_storage.py   #   Incident data persistence
│
├── frontend/                     # React dashboard application
│   ├── src/
│   │   ├── pages/                #   Page components (Dashboard, Report, Insights, etc.)
│   │   ├── components/           #   Reusable UI components (layout, charts, shadcn UI)
│   │   ├── hooks/                #   Custom React hooks
│   │   └── lib/                  #   API client & utilities
│   ├── package.json
│   └── vite.config.ts
│
├── scripts/                      # Executable scripts & utilities
│   ├── start_unified_server.py   #   ⭐ Main server (FastAPI + React on port 8080)
│   ├── start_system.py           #   System launcher (starts server cleanly)
│   ├── start_demo.py             #   Demo launcher (builds frontend + starts server)
│   ├── demo.py                   #   Quick agent workflow demo (terminal only)
│   ├── generate_performance_data.py  # Generate mock analytics data
│   └── ...                       #   Additional utilities
│
├── data/                         # JSON data stores
│   ├── real_incidents.json       #   Processed incident records
│   ├── analytics_data.json       #   Analytics & metrics data
│   └── rl_system_data.json       #   Reinforcement learning state
│
├── tests/                        # Automated test suite
│   └── test_agents.py            #   Agent unit & integration tests
│
├── docs/                         # Detailed documentation
│   ├── START_HERE.md
│   ├── SYSTEM_READY.md
│   └── VSCODE_SETUP.md
│
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

* **Python 3.11+**
* **Node.js 18+** and **npm**
* **Git**

### 1. Clone & Install

```bash
# Clone the repository
git clone <repository-url>
cd AGENTATHON

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API key (one or both):
# OPENAI_API_KEY=sk-...
# GROQ_API_KEY=gsk_...
```

> **💡 Tip:** The system works with simulated responses if no API key is provided, but real LLM responses require a valid key.

### 3. Run the System

#### Option A: Full Demo (Recommended)
Builds the React frontend and starts the unified server on port **8080**:
```bash
python scripts/start_demo.py
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser.

#### Option B: Clean System Start
Cleans previous incident data and launches the unified server:
```bash
python scripts/start_system.py
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser.

#### Option C: Quick Agent-Only CLI Demo
To see the 5-agent LangGraph workflow run entirely in your terminal:
```bash
python scripts/demo.py
```

---

## 🌐 API Reference

The FastAPI backend exposes the following RESTful endpoints on port `8080`:

### Incident Management
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/incidents` | Submit a new incident report |
| `GET` | `/api/v1/incidents` | List all incidents |
| `GET` | `/api/v1/incidents/{id}` | Get incident details by ID |
| `GET` | `/api/v1/incidents/{id}/status` | Get real-time processing status |
| `POST` | `/api/v1/incidents/upload-image` | Upload incident image with validation |

### Analytics & Insights
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/analytics/summary` | Overall dashboard metrics summary |
| `GET` | `/api/analytics/trends` | Temporal trends and category breakdown |
| `GET` | `/api/analytics/performance` | AI vs Human performance comparisons |

### Human Review Queue
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/review/queue` | Get incidents flagged for human validation |
| `POST` | `/api/v1/review/{id}/approve` | Approve a flagged incident |
| `POST` | `/api/v1/review/{id}/reject` | Reject a flagged incident |

> **Interactive API Docs (Swagger UI):** Available at **[http://localhost:8080/docs](http://localhost:8080/docs)** when the server is running.

---

## 🧪 Testing

The codebase includes a comprehensive test suite covering all agent logic, workflow orchestration, and safety rules:

```bash
# Run all tests
python -m pytest tests/ -v

# Run agent-specific tests
python tests/test_agents.py
```

---

## 🛡️ Safety & Policy Boundaries

Designed for secure, compliant educational environments:

* **Title IX compliance** — Filters, flags, and directs harassment/discrimination reports correctly.
* **FERPA compliance** — Restricts access to student records and enforces confidentiality.
* **Harmful action blocking** — Safety & Policy agent immediately blocks plans containing unsafe steps.
* **Spam & Gibberish filtering** — Prevents system abuse using integrated classifiers.
* **Human-in-the-loop escalation** — Automatically flags borderline or high-severity cases for manual approval.

---

## 📄 License

This project is licensed under the MIT License. Built with ❤️ for Campus Safety and Incident Response at **Agentathon 2025** (My First College Hackathon).
