---
title: Taby Tutora de Matemática
emoji: 📚
colorFrom: green
colorTo: blue
sdk: gradio
app_file: app.py
---

# chatbot-matematicas-jhirosedu
Chatbot de Matemáticas para Jhiro's Edu, enfocado en el CNB de Guatemala.

## Descripción
Este proyecto es un chatbot de matemáticas diseñado para estudiantes de 1º, 2º y 3º básico del Instituto Experimental de Educación Básica con Orientación Ocupacional. 

Utiliza la API de **GROQ** (con un backend seguro en Python/Flask) para proporcionar respuestas amigables y pedagógicas basadas en el **Currículo Nacional Base (CNB)** de Guatemala.

## Características
- **Taby Tutora de Matemática:** Un asistente de IA con personalidad amigable y motivadora.
- **Base de conocimiento CNB:** Respuestas adaptadas a los temas del CNB de 1º a 3º básico.
- **Interfaz Web (Frontend):** Desarrollada en HTML/CSS/JavaScript.
- **Backend Seguro (Proxy):** Implementado con Flask en Python, para proteger la API Key de GROQ.
- **Despliegue Gratuito:** Alojado en Hugging Face Spaces.

## Arquitectura
- **Frontend:** `index.html` (HTML, CSS, JavaScript)
- **Backend:** `app.py` (Flask en Python)
- **API de LLM:** GROQ (con modelos como `llama-3.3-70b-versatile`)
- **Hosting:** Hugging Face Spaces
- **Gestión de la API Key:** Protegida como secreto en Hugging Face Spaces.



## Estado Actual (22 de febrero de 2026)
- **Fracaso Inicial con LangChain/Colab:** Se experimentaron dificultades con la ejecución de prototipos en Google Colab debido a problemas de compatibilidad de versiones y limitaciones de rendimiento en CPU. Se generó frustración inicial, pero sirvió de aprendizaje.
- **Transición a Estrategia Claude/GROQ:** Se adoptó una nueva estrategia más robusta y compatible con la gratuidad: usar la API de GROQ con un backend proxy en Hugging Face Spaces.
- **Funcionalidad Local:** El chatbot funciona localmente con la API de GROQ.
- **API Key Oculta:** La API Key de GROQ ya no está expuesta en el `index.html` del frontend.
- **Despliegue HF Spaces Pendiente:** Se están realizando los ajustes finales para el despliegue correcto.
- **Problema de Detección `app_file`:** Hugging Face Spaces no detectaba `app.py` como el archivo principal debido a una configuración de SDK incorrecta. 
    - **Solución:** Se cambió el `sdk` a `gradio` y se ajustó `app.py` para servir la interfaz estática dentro del entorno.

## Próximos Pasos (Pendientes)
* Confirmar que `app.py`, `requirements.txt`, `index.html` y la carpeta `assets` estén correctamente subidos a la raíz del repositorio de GitHub.
* Verificar que Hugging Face Spaces detecte los cambios y despliegue el chatbot correctamente.
* Pruebas finales del chatbot desplegado en línea.
