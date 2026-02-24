from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import gradio as gr # ¡Nueva importación!

# Ajusta el static_folder y static_url_path para que Flask sirva los archivos correctamente
# dentro del entorno de Hugging Face Space si es necesario.
# Por defecto, Hugging Face Spaces sirve los archivos estáticos desde la raíz
# cuando el sdk es 'gradio' y 'output_dir' es '.'

app = Flask(__name__) # Ya no necesitamos static_folder aquí si Gradio lo maneja, o lo manejamos con send_from_directory

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

# Rutas para servir archivos estáticos (frontend)
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    # Esto servirá index.html si se solicita la raíz, y otros archivos como assets
    # Para la raíz, send_from_directory ya maneja index.html
    # Para assets, necesitamos una ruta específica
    if filename.startswith('assets/'):
        return send_from_directory('.', filename) # Sirve desde la raíz

    return send_from_directory('.', filename)


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


# Función dummy para Gradio que sirve la aplicación Flask
# En Hugging Face Spaces con sdk:gradio, el app.py DEBE devolver una interfaz de Gradio.
# La solución más sencilla para integrar nuestra app Flask es que Gradio la contenga en un iframe.

import threading
import time

class FlaskThread(threading.Thread):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance

    def run(self):
        # Iniciar la aplicación Flask en un puerto específico
        # Usamos 7861 para evitar conflictos con el puerto por defecto de Gradio 7860
        self.app.run(host="0.0.0.0", port=7861, debug=False)

if __name__ == "__main__":
    # Iniciar Flask en un hilo separado
    flask_thread = FlaskThread(app)
    flask_thread.start()

    # Dar un pequeño tiempo para que Flask se inicie
    time.sleep(2)

    with gr.Blocks(title="Taby Tutora de Matemática - Instituto Experimental") as demo:
        gr.HTML(value="""
            <h1 style="text-align: center; margin-top: 20px;">Cargando Taby Tutora...</h1>
            <p style="text-align: center;">Si no ves el chatbot en unos segundos, puede haber un error en el backend.</p>
            <iframe src="http://127.0.0.1:7861/" style="width: 100%; height: 80vh; border: none;"></iframe>
            <p style="text-align: center; font-size: 0.8em; color: gray;">
                El chatbot se carga dentro de un iframe. Si no funciona, verifica los logs.
            </p>
        """)
        # El iframe apunta al puerto donde Flask se está ejecutando.
        # En Hugging Face Spaces, el localhost se mapea correctamente.

    # Gradio lanzará la interfaz. Hugging Face Spaces usará el puerto 7860 por defecto.
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))

