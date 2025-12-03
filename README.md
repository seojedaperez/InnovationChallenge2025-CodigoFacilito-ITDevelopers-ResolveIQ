# ResolveIQ - Autonomous AI Customer Service Platform

ResolveIQ is an intelligent helpdesk solution that uses autonomous AI agents, advanced orchestration, and Azure cognitive services to revolutionize customer support and internal assistance.

## 🚀 Technologies and Architecture

The system is built on a modern microservices architecture, clearly separating the frontend from the backend, and heavily relying on the Azure cloud for its cognitive capabilities.

### 🧠 Specific Functionalities and Their Technologies

The following table details which specific technology powers each key capability of the system:

| Functionality | Technology / Library | Technical Description |
|---------------|----------------------|---------------------|
| **Text Translator** | **Azure OpenAI (GPT-4o)** | The LLM model detects and generates responses natively in the user's language. |
| **Article Translator** | **Azure OpenAI (GPT-4o)** | Dynamic summarization and translation of knowledge base documents on demand. |
| **Speech-to-Text (STT)** | **Web Speech API / Azure Speech SDK** | Uses the browser's native API for low latency, with built-in support for `microsoft-cognitiveservices-speech-sdk`. |
| **Text-to-Speech (TTS)** | **Web Speech API** | Real-time speech synthesis using the user's browser capabilities. |
| **User Login** | **Azure AD + MSAL** | Secure authentication via the Microsoft Authentication Library (`@azure/msal-react`) against Azure Active Directory. |
| **Image-to-Text (OCR)** | **GPT-4o Vision** | Multimodal analysis of images to extract text and visual context. |
| **Word/PDF to Text** | **python-docx / pypdf** | Backend document processing for content extraction and subsequent AI analysis. |
| **IP/Country Detection** | **ipapi.co** | External API consumed from the frontend for user geolocation. |
| **Word Blocking** | **Azure Content Safety** | Severity filter for hate, violence, sexual, and self-harm content. |
| **Email Sending** | **Azure Communication Services** | Programmatic sending of email notifications via `azure-communication-email`. |
| **Jailbreak Detection** | **LLM Evaluator + Regex** | Hybrid system: Local regex patterns + a dedicated LLM evaluator agent for complex attempts. |
| **Jailbreak Detection** | **LLM Evaluator + Regex** | Hybrid system: Local regex patterns + a dedicated LLM evaluator agent for complex attempts. |
| **Orchestration** | **Azure AI Foundry + Semantic Kernel** | Management of the agent lifecycle and planning of complex tasks. |
| **Stability and Resilience** | **AsyncIO + Tenacity Pattern** | Non-blocking architecture with intelligent retry logic and exponential backoff for external services. |

---

### 💻 Frontend (Client)

Developed with **React** and **TypeScript**, focused on a premium and accessible user experience.

*   **Core:** React 18, TypeScript, Vite (Build tool).
*   **UI/UX:**
    *   `@fluentui/react-components`: Microsoft's official design system.
    *   `framer-motion`: Fluid animations and transitions.
    *   `three`: 3D element rendering (Particle Head).
    *   `reactflow`: Real-time reasoning graph visualization.
*   **State and Data:**
    *   `@tanstack/react-query`: Asynchronous state management and caching.
    *   `axios`: HTTP client.
*   **Security:**
    *   `@azure/msal-browser` & `@azure/msal-react`: Token and identity management.

### 🔧 Backend (Server)

High-performance RESTful API built with **Python** and **FastAPI**.

*   **Core:** Python 3.11+, FastAPI, Uvicorn.
*   **AI and Processing:**
    *   `openai`: Official client for GPT models.
    *   `azure-ai-contentsafety`: SDK for content moderation.
    *   `azure-search-documents`: Vector and semantic search (RAG).
    *   `semantic-kernel`: AI orchestration framework.
*   **Data and Storage:**
    *   `azure-cosmos`: Globally distributed NoSQL database for tickets and conversations.
    *   `redis`: High-performance cache for sessions and frequent responses.
*   **File Processing:**
    *   `python-docx`: Word file parsing.
    *   `pypdf`: Text extraction from PDFs.
*   **Security:**
    *   `python-jose`: Validation and decoding of JWT tokens (Azure AD).
    *   `azure-identity`: Managed credentials and identity management.

### ☁️ Azure Infrastructure

The deployment uses PaaS services for scalability and zero maintenance.

1.  **Azure OpenAI Service:** The intelligence engine (GPT-4o, o1-preview models).
2.  **Azure AI Search:** Vector knowledge base for RAG (Retrieval-Augmented Generation).
3.  **Azure Cosmos DB:** Globally distributed data persistence.
4.  **Azure Content Safety:** Real-time security and moderation layer.
5.  **Azure Monitor / App Insights:** Observability and distributed tracing.

## 🛡️ Security and Compliance

*   **Authentication:** Full OAuth 2.0 / OIDC flow.
*   **Data Validation:** Pydantic for strict schemas in the backend.
*   **Content Protection:** Double-layer verification (Azure Service + LLM Check) before processing any input.

## 📦 Local Installation

1.  **Clone the repository.**
2.  **Backend:**
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn src.api.main:app --reload --port 5000
    ```
3.  **Frontend:**
    ```bash
    cd frontend
    npm install --legacy-peer-deps
    npm run dev
    ```
