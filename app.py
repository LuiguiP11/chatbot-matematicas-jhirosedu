from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_folder='.', static_url_path='') # Sirve archivos estáticos desde la raíz

# Lee la API Key de GROQ desde una variable de entorno
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Modelo de GROQ (puedes cambiarlo si deseas otro de los disponibles en Groq)
MODEL = "llama-3.3-70b-versatile" # O "llama-3.3-8b-8192" para una respuesta más rápida si es necesario
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Contenido del CNB para el system prompt (extracto de ejemplo)
SYSTEM_PROMPT = """
Eres "Taby Tutora de Matemática", un asistente educativo amigable, paciente y motivador para estudiantes de 1º, 2º y 3º básico del Instituto Experimental de Educación Básica con Orientación Ocupacional (Guatemala).

TEMAS QUE PUEDES RESPONDER según el CNB de Guatemala:

1º Básico:
• Números Naturales y Enteros (operaciones y propiedades).
• Fracciones y Decimales.
• Razones, Proporciones y Porcentajes.
• Álgebra introductoria (expresiones y ecuaciones de primer grado).
• Geometría (figuras planas, perímetro y área).
• Estadística descriptiva (tablas, gráficas, medidas de tendencia central).

2º Básico:
• Números Reales (racionales e irracionales).
• Álgebra (productos notables, factorización, ecuaciones lineales y cuadráticas).
• Geometría (triángulos, polígonos, cuerpos geométricos, teorema de Pitágoras).
• Funciones lineales y cuadráticas.
• Estadística y Probabilidad.

3º Básico:
• Números Complejos.
• Álgebra avanzada (ecuaciones, desigualdades, sistemas de ecuaciones).
• Funciones (lineales, cuadráticas, exponenciales, logarítmicas).
• Trigonometría (razones y funciones trigonométricas).
• Geometría analítica.
• Estadística inferencial.

REGLAS ESTRICTAS:
1. Solo respondes preguntas de los temas matemáticos del CNB listados arriba. Si el tema no corresponde, informa amablemente que solo puedes ayudar con matemáticas de 1º a 3º básico.
2. NUNCA des respuestas directas a tareas, ejercicios o exámenes. Guía al estudiante paso a paso con preguntas que le ayuden a descubrir la respuesta por sí mismo.
3. Usa lenguaje sencillo, ejemplos cotidianos (si es posible con contexto guatemalteco) y un tono alentador.
4. Mantén respuestas concisas (máximo 3-4 párrafos o pasos).
5. Sé respetuoso y positivo en todo momento.
"""

# Ruta para servir el index.html principal
@app.route("/")
def serve_index():
    return send_from_directory('.', 'index.html')

# Ruta para servir archivos estáticos (CSS, JS, imágenes)
@app.route("/assets/<path:path>")
def serve_assets(path):
    return send_from_directory('assets', path)

@app.route("/chat", methods=["POST"])
def chat():
    if not GROQ_API_KEY:
        return jsonify({"error": "GROQ_API_KEY no configurada en el servidor."}), 500

    user_message = request.json.get("message")
    conversation_history = request.json.get("history", [])

    if not user_message:
        return jsonify({"error": "Mensaje de usuario vacío"}), 400

    # Construir el historial para GROQ (OpenAI compatible)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in conversation_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        payload = {
            "model": MODEL,
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Lanza una excepción para errores HTTP

        groq_data = response.json()
        bot_text = groq_data["choices"][0]["message"]["content"]
        return jsonify({"response": bot_text})

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error de conexión con la API de GROQ: {e}")
        return jsonify({"error": f"Error de conexión con GROQ: {e}"}), 500
    except KeyError as e:
        app.logger.error(f"Estructura de respuesta inesperada de GROQ: {e}")
        return jsonify({"error": f"Error en la respuesta de GROQ: {e}"}), 500
    except Exception as e:
        app.logger.error(f"Error inesperado en el backend: {e}")
        return jsonify({"error": f"Error inesperado: {e}"}), 500

# Esta parte es específica para Hugging Face Spaces
# Hugging Face Spaces usa el puerto 7860 para Gradio/Streamlit por defecto
# Para Flask, el puerto suele ser 5000, pero HF Spaces se encarga de la redirección
# Lo importante es que el __name__ == "__main__" no se ejecute en el entorno de HF Spaces
# ya que HF Spaces tiene su propio método de ejecución (gunicorn, uwsgi, etc.)

# Por lo tanto, no necesitamos el if __name__ == "__main__": app.run(...)
# en un entorno de Hugging Face Spaces con sdk:python o sdk:gradio
# La plataforma se encargará de ejecutar la aplicación Flask.
