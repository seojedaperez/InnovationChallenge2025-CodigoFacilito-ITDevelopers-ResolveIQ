# ResolveIQ - Plataforma de Servicio al Cliente con IA Autónoma

ResolveIQ es una solución de mesa de ayuda inteligente que utiliza agentes de IA autónomos, orquestación avanzada y servicios cognitivos de Azure para revolucionar la atención al cliente y el soporte interno.

## 🚀 Tecnologías y Arquitectura

El sistema está construido sobre una arquitectura moderna de microservicios, separando claramente el frontend del backend, y apoyándose fuertemente en la nube de Azure para las capacidades cognitivas.

### 🧠 Funcionalidades Específicas y Sus Tecnologías

A continuación se detalla qué tecnología específica impulsa cada capacidad clave del sistema:

| Funcionalidad | Tecnología / Librería | Descripción Técnica |
|---------------|----------------------|---------------------|
| **Traductor de Textos** | **Azure OpenAI (GPT-4o)** | El modelo LLM detecta y genera respuestas en el idioma del usuario nativamente. |
| **Traductor de Artículos** | **Azure OpenAI (GPT-4o)** | Resumen y traducción dinámica de documentos de la base de conocimiento bajo demanda. |
| **Voz a Texto (STT)** | **Web Speech API / Azure Speech SDK** | Utiliza la API nativa del navegador para baja latencia, con soporte integrado para `microsoft-cognitiveservices-speech-sdk`. |
| **Texto a Voz (TTS)** | **Web Speech API** | Síntesis de voz en tiempo real utilizando las capacidades del navegador del usuario. |
| **Login de Usuario** | **Azure AD + MSAL** | Autenticación segura mediante Microsoft Authentication Library (`@azure/msal-react`) contra Azure Active Directory. |
| **Imagen a Texto (OCR)** | **GPT-4o Vision** | Análisis multimodal de imágenes para extraer texto y contexto visual. |
| **Word/PDF a Texto** | **python-docx / pypdf** | Procesamiento de documentos en el backend para extracción de contenido y posterior análisis por IA. |
| **Detección de IP/País** | **ipapi.co** | API externa consumida desde el frontend para geolocalización del usuario. |
| **Bloqueo de Palabras** | **Azure Content Safety** | Filtro de severidad para odio, violencia, sexual y autolesiones. |
| **Envío de Correos** | **Azure Communication Services** | Envío programático de notificaciones por correo electrónico mediante `azure-communication-email`. |
| **Detección de Jailbreak** | **LLM Evaluator + Regex** | Sistema híbrido: Patrones regex locales + un agente evaluador LLM dedicado para intentos complejos. |
| **Detección de Jailbreak** | **LLM Evaluator + Regex** | Sistema híbrido: Patrones regex locales + un agente evaluador LLM dedicado para intentos complejos. |
| **Orquestación** | **Azure AI Foundry + Semantic Kernel** | Gestión del ciclo de vida de los agentes y planificación de tareas complejas. |
| **Estabilidad y Resiliencia** | **AsyncIO + Tenacity Pattern** | Arquitectura no bloqueante con lógica de reintentos inteligente y backoff exponencial para servicios externos. |

---

### 💻 Frontend (Cliente)

Desarrollado con **React** y **TypeScript**, enfocado en una experiencia de usuario premium y accesible.

*   **Core:** React 18, TypeScript, Vite (Build tool).
*   **UI/UX:**
    *   `@fluentui/react-components`: Sistema de diseño oficial de Microsoft.
    *   `framer-motion`: Animaciones fluidas y transiciones.
    *   `three`: Renderizado de elementos 3D (Particle Head).
    *   `reactflow`: Visualización de grafos de razonamiento en tiempo real.
*   **Estado y Datos:**
    *   `@tanstack/react-query`: Gestión de estado asíncrono y caché.
    *   `axios`: Cliente HTTP.
*   **Seguridad:**
    *   `@azure/msal-browser` & `@azure/msal-react`: Gestión de tokens e identidad.

### 🔧 Backend (Servidor)

API RESTful de alto rendimiento construida con **Python** y **FastAPI**.

*   **Core:** Python 3.11+, FastAPI, Uvicorn.
*   **IA y Procesamiento:**
    *   `openai`: Cliente oficial para modelos GPT.
    *   `azure-ai-contentsafety`: SDK para moderación de contenido.
    *   `azure-search-documents`: Búsqueda vectorial y semántica (RAG).
    *   `semantic-kernel`: Framework de orquestación de IA.
*   **Datos y Almacenamiento:**
    *   `azure-cosmos`: Base de datos NoSQL para tickets y conversaciones.
    *   `redis`: Caché de alto rendimiento para sesiones y respuestas frecuentes.
*   **Procesamiento de Archivos:**
    *   `python-docx`: Parsing de archivos Word.
    *   `pypdf`: Extracción de texto de PDFs.
*   **Seguridad:**
    *   `python-jose`: Validación y decodificación de tokens JWT (Azure AD).
    *   `azure-identity`: Gestión de credenciales e identidades gestionadas.

### ☁️ Infraestructura Azure

El despliegue utiliza servicios PaaS para escalabilidad y mantenimiento cero.

1.  **Azure OpenAI Service:** Motor de inteligencia (Modelos GPT-4o, o1-preview).
2.  **Azure AI Search:** Base de conocimiento vectorial para RAG (Retrieval-Augmented Generation).
3.  **Azure Cosmos DB:** Persistencia de datos globalmente distribuida.
4.  **Azure Content Safety:** Capa de seguridad y moderación en tiempo real.
5.  **Azure Monitor / App Insights:** Observabilidad y trazas distribuidas.

## 🛡️ Seguridad y Cumplimiento

*   **Autenticación:** Flujo OAuth 2.0 / OIDC completo.
*   **Validación de Datos:** Pydantic para esquemas estrictos en backend.
*   **Protección de Contenido:** Doble capa de verificación (Azure Service + LLM Check) antes de procesar cualquier input.

## 📦 Instalación Local

1.  **Clonar el repositorio.**
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
