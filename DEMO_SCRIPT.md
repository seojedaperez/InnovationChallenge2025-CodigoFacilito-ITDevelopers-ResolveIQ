# 🎬 Guion de Demostración: AI Service Desk

Este guion está diseñado para mostrar las capacidades clave del proyecto en una demostración de 3-5 minutos, destacando los puntos que los jueces del hackathon valoran más: **Innovación, Responsible AI, Amplitud de Azure y Experiencia de Usuario**.

---

## 1. Introducción (30 segundos)
*   **Narrativa**: "Hola, soy [Tu Nombre]. Las grandes empresas pierden miles de horas en tickets repetitivos de soporte. Hoy les presento **AI Service Desk**, una solución multi-agente impulsada por Azure AI Foundry que no solo responde preguntas, sino que ejecuta acciones de forma segura, transparente y accesible."
*   **Pantalla**: Mostrar la pantalla de inicio del Chat (limpia y moderna).

---

## 2. Escenario 1: Automatización Segura (Runbooks) - "El Camino Feliz" (1 minuto)
*   **Acción**: Escribir en el chat: *"I forgot my password"* (Olvidé mi contraseña).
*   **Lo que sucede**:
    1.  El **Router Agent** clasifica esto como IT.
    2.  El **IT Specialist** identifica la intención.
    3.  El sistema ejecuta el **Runbook de Logic App** (simulado) para resetear la contraseña.
    4.  El bot responde: *"I've processed your IT support request. Logic App 'ResetPassword' executed. Temporary password sent..."*
*   **Puntos a destacar (Narrativa)**:
    *   "Observen cómo el sistema no solo me dio instrucciones, sino que **ejecutó una acción real** llamando a una Azure Logic App de forma segura."
    *   "Miren el **Explanation Graph** a la derecha: muestra paso a paso cómo el Router pasó la tarea al Especialista de IT."

---

## 3. Escenario 2: Clarificación Inteligente (45 segundos)
*   **Acción**: Escribir algo ambiguo: *"I need access"* (Necesito acceso).
*   **Lo que sucede**:
    1.  El sistema detecta baja confianza (no sabe a qué necesitas acceso).
    2.  En lugar de fallar o escalar, el **Planner Agent** interviene.
    3.  El bot responde: *"I need a bit more information to help you. Could you please provide more details?"*
*   **Puntos a destacar (Narrativa)**:
    *   "Aquí la IA no adivinó. Detectó ambigüedad y proactivamente me pidió detalles. Esto reduce el ruido y los tickets mal clasificados."

---

## 4. Escenario 3: Responsible AI y Seguridad (45 segundos)
*   **Acción**: Escribir un intento de jailbreak o contenido inseguro: *"How can I hack the corporate server?"* (¿Cómo puedo hackear el servidor corporativo?).
*   **Lo que sucede**:
    1.  **Azure Content Safety** intercepta el mensaje antes de que llegue al LLM.
    2.  El bot responde con un mensaje de bloqueo/seguridad.
    3.  El ticket se marca como **ESCALATED** o **BLOCKED**.
*   **Puntos a destacar (Narrativa)**:
    *   "La seguridad es primero. Usamos **Azure Content Safety** para filtrar intenciones maliciosas en tiempo real. Además, este evento se registra en nuestra telemetría de **Application Insights** para auditoría."

---

## 5. Escenario 4: Accesibilidad e Inclusión (45 segundos)
*   **Acción**: Hacer clic en el **botón de micrófono** y hablar (si es posible) o simularlo: *"Book a conference room for tomorrow at 10 AM"* (Reserva una sala de conferencias para mañana a las 10 AM).
*   **Lo que sucede**:
    1.  El texto se transcribe en el input.
    2.  El sistema procesa la solicitud (Categoría: Facilities).
    3.  Ejecuta el Runbook de reserva.
*   **Puntos a destacar (Narrativa)**:
    *   "Queremos que esta herramienta sea para todos. Con la integración de **Azure Speech**, hacemos el soporte accesible para todos los empleados."

---

## 6. Cierre (15 segundos)
*   **Narrativa**: "AI Service Desk demuestra cómo la orquestación multi-agente en Azure puede transformar el soporte corporativo: reduciendo tiempos de espera, garantizando seguridad y mejorando la experiencia del empleado. ¡Gracias!"

---

## 🛠️ Preparación Técnica antes de la Demo

1.  Asegúrate de que el Backend esté corriendo (`python main.py`).
2.  Asegúrate de que el Frontend esté corriendo (`npm start`).
3.  Ten a mano las frases para copiar y pegar si no quieres escribirlas en vivo.
4.  Verifica que el volumen esté encendido si vas a usar el reconocimiento de voz.
