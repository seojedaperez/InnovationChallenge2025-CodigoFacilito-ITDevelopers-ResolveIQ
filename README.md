# ResolveIQ - Autonomous Enterprise Service Desk 🤖🚀

**ResolveIQ** is an enterprise-grade **Auto-resolving Service Desk** solution designed for the **Microsoft Innovation Challenge 2025**. It leverages an advanced **Multi-Agent** architecture orchestrated by **Azure AI Foundry Agent Service**, integrating over 20 Azure services to resolve IT, HR, and Facilities tickets autonomously, securely, and efficiently.

---

## 📊 Pitch Deck Overview

**The Problem:**
Traditional enterprise service desks are overwhelmed by repetitive requests (password resets, leave inquiries, room bookings), leading to slow response times, high operational costs, and frustrated employees. Human agents spend too much time on Level 1 tickets instead of complex issues.

**The Solution:**
**ResolveIQ** transforms internal support from reactive to proactive using a **Multi-Agent System**.
*   **Autonomous Resolution:** Agents don't just chat; they *act* (reset passwords, book rooms) using secure Runbooks.
*   **Ambiguity Handling:** Capable of understanding and executing multi-intent requests (e.g., "I need a new mouse and I want to book a vacation") in parallel.
*   **Trust & Safety:** Built-in "Guardrails" with Azure Content Safety to prevent toxicity and protect PII, ensuring enterprise-grade compliance.

**Why Now?**
Leveraging the power of **Azure AI Foundry** and **Semantic Kernel**, we move beyond simple chatbots to true **Agentic AI** that plans, reasons, and executes complex workflows with full observability.

---

## 🌟 Key Features

*   **Multi-Agent Orchestration**: Uses a "Planner" to break down tasks, a "Router" to classify tickets, and "Specialists" (IT, HR, Facilities) to resolve them.
*   **Secure Automation (Runbooks)**: Autonomous execution of tasks like password resets and room bookings when confidence is high.
*   **Intelligent Clarification**: Agents proactively ask for missing details if a request is ambiguous before escalating.
*   **Responsible AI**: Deep integration with **Azure Content Safety** to detect toxicity, jailbreaks, and protect sensitive data (PII).
*   **Semantic Search (RAG)**: Enterprise knowledge retrieval using **Azure AI Search** with vector capabilities.
*   **Modern UI**: **React** frontend with **Fluent UI** and real-time decision graph visualization (**Explanation Graph**).
*   **Comprehensive Dashboard**: Includes 'My Tickets', 'Knowledge Base', 'Analytics', and 'Settings' views.
*   **Accessibility First**: WCAG 2.1 compliant with high contrast modes, text-to-speech (TTS), and adjustable font sizes.
*   **Internationalization (i18n)**: Full support for English and Spanish, with dynamic language switching.
*   **Theme Support**: Consistent Light and Dark mode experience.
*   **Infrastructure as Code**: Automated deployment using **Bicep**.

---

## 🚀 Installation & Running

Follow these steps to run the project locally.

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Git
*   Active Azure Subscription

### 1. Clone the Repository
```bash
git clone <repo-url>
cd AzureAIDevs-antigravity
```

### 2. Backend Setup
Open a terminal in the root directory:

```bash
# Install dependencies
python -m pip install -r backend/requirements.txt

# Run the backend server
python -m uvicorn backend.src.api.main:app --reload --port 5000
```
The backend will be running at: `http://localhost:5000`

### 3. Frontend Setup
Open a new terminal:

```bash
cd frontend

# Install dependencies (if not already installed)
npm install

# Run the development server
npm run dev
```
The frontend will be available at: `http://localhost:3000`

---

## 🏗️ System Architecture

The system follows an event-driven, agent-oriented microservices architecture:

1.  **Frontend (React + Vite)**:
    *   Chat interface for users.
    *   Agent reasoning graph visualization (React Flow).
    *   REST API communication.

2.  **Backend (FastAPI + Python)**:
    *   **API Gateway**: Manages frontend requests.
    *   **Agent Orchestrator**: Coordinates agent execution using **Azure AI Foundry SDK**.
    *   **Services Layer**: Abstractions for Azure Search, Cosmos DB, and Content Safety.

3.  **Data & AI Layer (Azure)**:
    *   **Azure AI Foundry**: Agent hosting and execution (GPT-4o).
    *   **Azure Cosmos DB**: Ticket and conversation history storage.
    *   **Azure AI Search**: Indexed knowledge base.
    *   **Azure Content Safety**: Real-time content moderation.

---

## 💻 Tech Stack

### Backend 🐍
*   **Language**: Python 3.10+
*   **API Framework**: FastAPI.
*   **AI & Agents**: Azure AI Foundry Agent Service, Azure OpenAI (GPT-4o), Semantic Kernel.
*   **Database**: Azure Cosmos DB.
*   **Search**: Azure AI Search.
*   **Security**: Azure Content Safety, Azure Identity.

### Frontend ⚛️
*   **Framework**: React 18 (Vite).
*   **Language**: TypeScript.
*   **UI Library**: Fluent UI React Components.
*   **Visualization**: React Flow.

---

## 📄 License
MIT
