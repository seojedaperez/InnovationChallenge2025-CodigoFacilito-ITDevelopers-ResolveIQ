# ResolveIQ - The Autonomous Enterprise Service Mesh 🤖🚀

**ResolveIQ** es una solución de **Service Desk de Auto-resolución** de nivel empresarial, diseñada para el **Microsoft Innovation Challenge 2025**. Utiliza una arquitectura avanzada de **Múltiples Agentes** orquestada por **Azure AI Foundry Agent Service**, integrando más de 20 servicios de Azure para resolver tickets de TI, RRHH y Mantenimiento de forma autónoma, segura y eficiente.

## 🌟 Características Principales

## 🌟 Características Principales

*   **Orquestación Multi-Agente**: Utiliza un "Planner" para descomponer tareas, un "Router" para clasificar tickets y "Specialists" (TI, RRHH, Instalaciones) para resolverlos.
*   **Automatización Segura (Runbooks)**: Ejecución autónoma de tareas como restablecimiento de contraseñas y reserva de salas cuando la confianza es alta.
*   **Clarificación Inteligente**: Los agentes solicitan detalles faltantes al usuario si la solicitud es ambigua, antes de escalar.
*   **Inteligencia Artificial Responsable**: Integración profunda con **Azure Content Safety** para detectar toxicidad, jailbreaks y proteger datos sensibles (PII).
*   **Búsqueda Semántica (RAG)**: Recuperación de conocimiento empresarial mediante **Azure AI Search** con vectores.
*   **Interfaz Moderna**: Frontend en **React** con **Fluent UI** y visualización de grafos de decisión en tiempo real (**Explanation Graph**).
*   **Infraestructura como Código**: Despliegue automatizado mediante **Bicep**.

---

## 🏗️ Arquitectura del Sistema

El sistema sigue una arquitectura de microservicios orientada a eventos y agentes:

1.  **Frontend (React + Vite)**:
    *   Interfaz de chat para usuarios.
    *   Visualización del grafo de razonamiento de los agentes (React Flow).
    *   Comunicación con el backend vía API REST.

2.  **Backend (FastAPI + Python)**:
    *   **API Gateway**: Gestiona las solicitudes del frontend.
    *   **Agent Orchestrator**: Coordina la ejecución de agentes usando **Azure AI Foundry SDK**.
    *   **Services Layer**: Abstracciones para Azure Search, Cosmos DB, y Content Safety.

3.  **Capa de Datos e IA (Azure)**:
    *   **Azure AI Foundry**: Alojamiento y ejecución de agentes (GPT-4o).
    *   **Azure Cosmos DB**: Almacenamiento de tickets e historial de conversaciones.
    *   **Azure AI Search**: Base de conocimiento indexada.
    *   **Azure Content Safety**: Moderación de contenido en tiempo real.

---

## 💻 Tecnologías Utilizadas

### Backend 🐍
*   **Lenguaje**: Python 3.10+
*   **Framework API**: FastAPI (Alto rendimiento, asíncrono).
*   **IA & Agentes**:
    *   **Azure AI Foundry Agent Service**: Orquestación nativa de agentes.
    *   **Azure OpenAI**: Modelos GPT-4o y Embeddings.
    *   **Semantic Kernel**: Framework de integración (como fallback/complemento).
*   **Base de Datos**: Azure Cosmos DB (NoSQL).
*   **Búsqueda**: Azure AI Search (Vector Search).
*   **Seguridad**: Azure Content Safety, Azure Identity.

### Frontend ⚛️
*   **Framework**: React 18 (Vite).
*   **Lenguaje**: TypeScript.
*   **UI Library**: Fluent UI React Components (Estándar de diseño de Microsoft).
*   **Visualización**: React Flow (Para el grafo de explicación de agentes).
*   **Estado**: React Hooks & Context.
*   **Comunicación**: Axios.

---

## 🔑 Configuración de Credenciales

Para que el sistema funcione, necesitas configurar las variables de entorno en el archivo `.env` dentro de la carpeta `backend/`.

### Paso a Paso para Obtener las Credenciales:

1.  **Azure AI Foundry & OpenAI**:
    *   Ve a [Azure AI Foundry Portal](https://ai.azure.com/).
    *   Crea un proyecto nuevo.
    *   En "Settings" o "Project settings", copia el **Project Connection String**.
    *   Despliega un modelo `gpt-4o` y copia el nombre del despliegue.
    *   *Variable*: `AZURE_AI_PROJECT_CONNECTION_STRING`, `AZURE_OPENAI_GPT4O_DEPLOYMENT`.

2.  **Azure AI Search**:
    *   Ve al recurso de Search en Azure Portal.
    *   En "Keys", copia la **Admin Key**.
    *   En "Overview", copia la **Url**.
    *   *Variables*: `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_KEY`.

3.  **Azure Cosmos DB**:
    *   Ve al recurso de Cosmos DB.
    *   En "Keys", copia la **URI** y la **Primary Key**.
    *   *Variables*: `AZURE_COSMOS_ENDPOINT`, `AZURE_COSMOS_KEY`.

4.  **Azure Content Safety**:
    *   Crea un recurso de Content Safety.
    *   Copia el **Endpoint** y la **Key**.
    *   *Variables*: `AZURE_CONTENT_SAFETY_ENDPOINT`, `AZURE_CONTENT_SAFETY_KEY`.

**Ejemplo de archivo `.env`:**
```env
AZURE_AI_PROJECT_CONNECTION_STRING="<tu_connection_string>"
AZURE_OPENAI_GPT4O_DEPLOYMENT="gpt-4o"
AZURE_SEARCH_ENDPOINT="https://<tu-search>.search.windows.net"
AZURE_SEARCH_KEY="<tu_key>"
AZURE_COSMOS_ENDPOINT="https://<tu-cosmos>.documents.azure.com:443/"
AZURE_COSMOS_KEY="<tu_key>"
AZURE_CONTENT_SAFETY_ENDPOINT="https://<tu-safety>.cognitiveservices.azure.com/"
AZURE_CONTENT_SAFETY_KEY="<tu_key>"
```

---

## 🚀 Instalación y Ejecución

Sigue estos pasos para ejecutar el proyecto en tu máquina local.

### Prerrequisitos
*   Python 3.10 o superior.
*   Node.js 18 o superior.
*   Git.
*   Una suscripción de Azure activa.

### 1. Clonar el Repositorio
```bash
git clone <url-del-repo>
cd AzureAIDevs-antigravity
```

### 2. Configurar el Backend
```bash
cd backend
# Crear entorno virtual (opcional pero recomendado)
python -m venv venv
# Activar entorno (Windows)
.\venv\Scripts\activate
# Activar entorno (Mac/Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el servidor
python -m src.api.main
```
El backend estará corriendo en: `http://localhost:5000`

### 3. Configurar el Frontend
Abre una nueva terminal:
```bash
cd frontend
# Instalar dependencias
npm install

# Ejecutar el servidor de desarrollo
npm run dev
```
El frontend estará disponible en: `http://localhost:3000`

### 4. Verificar la Instalación
1.  Abre tu navegador en `http://localhost:3000`.
2.  Deberías ver la interfaz de "ResolveIQ".
3.  Escribe "Hola" en el chat. Si las credenciales están bien configuradas, el agente responderá. Si no, verás un mensaje de error o una respuesta simulada (Mock) si el modo fallback está activo.

---

## 📈 Tendencias y Futuro (2025)

Este proyecto está alineado con las últimas tendencias en IA Agentica:
*   **Agentic Patterns**: Uso de patrones de diseño de agentes (Planner-Executor) en lugar de simples cadenas de prompts.
*   **Observabilidad de IA**: El "Explanation Graph" proporciona transparencia total sobre cómo la IA toma decisiones, crucial para la adopción empresarial.
*   **Seguridad Primero**: La implementación de "Guardrails" con Azure Content Safety es un estándar moderno para prevenir alucinaciones y respuestas inapropiadas.

---

## 🤝 Contribución
Las contribuciones son bienvenidas. Por favor, abre un Issue o un Pull Request para discutir cambios mayores.

## 📄 Licencia
MIT
