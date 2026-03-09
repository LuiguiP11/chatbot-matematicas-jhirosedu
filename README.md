---
title: Taby Tutora de Matemática
emoji: 📚
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
---

# Taby Tutora de Matemática - Jhiro's Edu 📐✨

¡Bienvenido al repositorio oficial de **Taby**, la tutora inteligente de matemáticas! ❤️

Este proyecto está diseñado específicamente para estudiantes de **1º, 2º y 3º básico** del Instituto Experimental de Educación Básica con Orientación Ocupacional en Guatemala. Taby utiliza la potencia de **GROQ** (modelos Llama 3) para brindar una experiencia educativa motivadora, amigable y alineada con el **Currículo Nacional Base (CNB)**.

## 🚀 Despliegue en Hugging Face Spaces

Este chatbot está configurado para ejecutarse en un contenedor **Docker** para garantizar la máxima estabilidad y control de dependencias.

- **SDK:** Docker
- **Puerto:** 7860
- **Backend:** Flask (Python 3.10)
- **Frontend:** HTML5, CSS3 y JavaScript Moderno

## 🛠️ Arquitectura y Tecnologías

- **IA Generativa:** GROQ API (Llama 3.3 70B)
- **Procesamiento de Documentos:** PyPDF2 (para integrar el CNB de Guatemala)
- **Interfaz de Usuario:** Diseño "Glassmorphism" responsivo y amigable.
- **Seguridad:** Las API Keys se gestionan mediante variables de entorno en el Space.

## 📁 Estructura del Proyecto

```text
.
├── app.py                # Servidor backend Flask y lógica de la IA
├── Dockerfile            # Configuración del contenedor
├── requirements.txt      # Dependencias de Python
├── cnb_matematicas.pdf   # Base de conocimiento (CNB Guatemala)
├── templates/
│   └── index.html        # Interfaz de usuario (Frontend)
└── static/
    └── assets/           # Imágenes y recursos visuales
```

## ❤️ Sobre el Proyecto
Taby es más que un chatbot; es una compañera de aprendizaje creada por **Jhiro's Edu** para demostrar que la tecnología y la pedagogía pueden unirse para transformar la educación.

© 2026 Jhiro's Edu | Todos los derechos reservados
