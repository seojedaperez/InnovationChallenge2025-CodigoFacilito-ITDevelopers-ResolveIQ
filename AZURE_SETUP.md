# ☁️ Guía de Configuración de Azure y Credenciales

Esta guía te llevará paso a paso para crear los recursos necesarios en Azure y obtener las credenciales para tu archivo `.env`.

---

## 1. Preparativos Iniciales
1.  Inicia sesión en el [Portal de Azure](https://portal.azure.com).
2.  **Nota Importante sobre el Grupo de Recursos**:
    *   No crees un grupo de recursos manualmente todavía.
    *   Cuando crees el proyecto en **Azure AI Foundry** (paso siguiente), Azure creará uno automáticamente para ti (generalmente llamado `rg-service-desk-agents` o similar).
    *   **Para todos los pasos siguientes (Search, Cosmos, etc.), asegúrate de seleccionar ESE mismo grupo de recursos** para mantener todo junto.
    *   **Región (Location)**: Selecciona siempre la misma región que tu proyecto de AI Foundry (ej. `East US 2`) para evitar latencia.

---

## 2. Azure AI Foundry (El Cerebro) 🧠
Este es el servicio principal que orquesta los agentes.

1.  Ve a [Azure AI Foundry Portal](https://ai.azure.com).
2.  Haz clic en **+ Create Project**.
3.  Llena los datos:
    *   **Project name**: `service-desk-agents`.
    *   **Hub**: Crea uno nuevo si no tienes.
4.  Una vez creado el proyecto, estarás en la vista general ("Overview").
5.  **Obtener la Connection String**:
    *   ⚠️ **Importante**: No está en la pantalla principal.
    *   Busca el icono de **Settings** (engranaje ⚙️) en la barra lateral izquierda (generalmente abajo).
    *   En la pestaña **Project details**, verás el campo **Project connection string**.
    *   Copia todo el valor (suele empezar por la región, ej: `eastus2.api...`).
    *   👉 Pégalo en tu `.env` como `AZURE_AI_PROJECT_CONNECTION_STRING`.

### Desplegar el Modelo GPT-4o
1.  En el mismo portal de AI Foundry, ve al menú izquierdo **Models + endpoints**.
2.  Haz clic en **+ Deploy model** > **Deploy base model**.
3.  Busca `gpt-4o`. Selecciónalo y dale a **Confirm**.
4.  En la configuración de despliegue:
    *   **Deployment name**: `gpt-4o` (¡Importante! Debe coincidir con tu `.env`).
    *   **Deployment type**: Standard.
    *   Haz clic en **Deploy**.
    *   👉 Asegúrate de que en tu `.env`, `AZURE_OPENAI_GPT4O_DEPLOYMENT` sea `gpt-4o`.

---

## 3. Azure AI Search (La Memoria) 📚
Para que los agentes puedan buscar en documentos.

1.  Vuelve al [Portal de Azure](https://portal.azure.com).
2.  Busca "AI Search" y haz clic en **Create**.
3.  **Configuración**:
    *   **Service name**: `search-service-desk-seojedaperez` (debe ser único).
    *   **Location**: La misma que tu proyecto (ej. `East US 2`).
    *   **Pricing tier**: `Basic` o `Standard` (el Free a veces tiene límites para vectores, pero para pruebas simples puede servir. Recomendado: Basic).
4.  Una vez creado, ve al recurso:
    *   **Endpoint**: Está en la vista "Overview". Copia la URL (ej. `https://xxx.search.windows.net`).
        *   👉 Pégalo en `AZURE_SEARCH_ENDPOINT`.
    *   **Keys**: Ve al menú izquierdo **Settings** > **Keys**.
    *   Copia la **Primary admin key**.
        *   👉 Pégalo en `AZURE_SEARCH_KEY`.

---

## 4. Azure Cosmos DB (La Base de Datos) 🗄️
Para guardar los tickets y el historial.

1.  En el Portal de Azure, busca "Azure Cosmos DB" > **Create**.
2.  Selecciona **Azure Cosmos DB for NoSQL**.
3.  **Configuración**:
    *   **Workload Type**: Selecciona **Development** o **Testing** (esto suele habilitar opciones más baratas).
    *   **Resource Group**: Selecciona `rg-service-desk-agents`.
    *   **Account Name**: `cosmos-service-desk-seojedaperez`.
    *   **Location**: La misma que tu proyecto (ej. `East US` o `East US 2`).
    *   **Capacity mode**: Serverless (más barato para desarrollo) o Provisioned.
    *   **Apply Free Tier Discount**: Selecciona **Apply** si está disponible.
    *   **Limit total account throughput**: Déjalo marcado si usas Provisioned.
4.  Haz clic en **Review + create** y luego en **Create**. Espera a que termine el despliegue.
5.  Una vez creado, ve al recurso:
    *   Ve al menú izquierdo **Settings** > **Keys**.
    *   **URI**: Copia la URI.
        *   👉 Pégalo en `AZURE_COSMOS_ENDPOINT`.
    *   **Primary Key**: Copia la clave primaria.
        *   👉 Pégalo en `AZURE_COSMOS_KEY`.

---

## 5. Azure Content Safety (La Seguridad) 🛡️
Para moderar contenido tóxico.

1.  En el Portal de Azure, busca "Content Safety" > **Create**.
2.  **Configuración**:
    *   **Name**: `safety-service-desk-seojedaperez`.
    *   **Location**: La misma que tu proyecto (ej. `East US 2`).
    *   **Pricing tier**: F0 (Free) o S0 (Standard).
3.  Una vez creado:
    *   Ve a **Resource Management** > **Keys and Endpoint**.
    *   **Endpoint**: Copia la URL.
        *   👉 Pégalo en `AZURE_CONTENT_SAFETY_ENDPOINT`.
    *   **Key 1**: Copia la clave.
        *   👉 Pégalo en `AZURE_CONTENT_SAFETY_KEY`.

---

## 6. Application Insights (Telemetría - Opcional) 📊
Para ver logs y auditoría.

1.  Busca "Application Insights" > **Create**.
2.  Una vez creado, en la vista "Overview", copia el **Connection String**.
    *   👉 Pégalo en `APPLICATIONINSIGHTS_CONNECTION_STRING`.

---

## ✅ Resumen del `.env` Final
Tu archivo `backend/.env` debería verse así:

```env
AZURE_AI_PROJECT_CONNECTION_STRING="<copiado de AI Foundry>"
AZURE_AI_PROJECT_NAME="service-desk-agents"

AZURE_OPENAI_GPT4O_DEPLOYMENT="gpt-4o"

AZURE_SEARCH_ENDPOINT="https://<tu-search>.search.windows.net"
AZURE_SEARCH_KEY="<tu-key>"
AZURE_SEARCH_INDEX_NAME="knowledge-base"

AZURE_COSMOS_ENDPOINT="https://<tu-cosmos>.documents.azure.com:443/"
AZURE_COSMOS_KEY="<tu-key>"
AZURE_COSMOS_DATABASE_NAME="servicedesk"

AZURE_CONTENT_SAFETY_ENDPOINT="https://<tu-safety>.cognitiveservices.azure.com/"
AZURE_CONTENT_SAFETY_KEY="<tu-key>"

APPLICATIONINSIGHTS_CONNECTION_STRING="<tu-connection-string>"
```
