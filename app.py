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
def run_flask_app():
    # Gradio solo necesita una función que pueda llamar.
    # Como nuestra app de Flask ya maneja las rutas y sirve el frontend,
    # no necesitamos que Gradio haga mucho aquí, solo que "ejecute" algo.
    # En un Space de Gradio, app.py se espera que defina una interfaz de Gradio.
    # La forma de integrar Flask es montarla como una aplicación WSGI.

    # Sin embargo, para la mayoría de los casos en HF Spaces con sdk:gradio,
    # simplemente servir el index.html desde Flask ya funciona.
    # Para el caso en que Gradio necesite una UI, podemos hacer una dummy.
    # Pero una forma más directa es simplemente ejecutar la app de Flask en el puerto
    # que Gradio espera, y HF Spaces se encarga de servir el index.html.

    # Descartamos la idea de montar Flask con Gradio directamente para simplificar.
    # La clave es que el archivo app.py se "ejecuta" y la app de Flask se levanta.
    # El sdk:gradio en el README.md parece que busca un archivo que lance Gradio.
    # Si tenemos una app de Flask, la mejor forma es con Dockerfile.

    # Si queremos mantener sdk:gradio y un app.py, entonces el app.py DEBE
    # devolver una UI de Gradio. Y Gradio puede embeber otras apps.

    # La solución más directa para que nuestro app.py de Flask funcione con sdk:gradio
    # es que la aplicación de Flask se monte como un "componente" de Gradio.

    # Reajustando para que Gradio lance la app de Flask.
    # Flask es una aplicación WSGI. Gradio tiene un componente para ello.

    with gr.Blocks() as demo:
        gr.HTML(value="""
            <h1 style="text-align: center; margin-top: 20px;">Cargando Taby Tutora...</h1>
            <p style="text-align: center;">Si no ves el chatbot en unos segundos, puede haber un error en el backend.</p>
        """)
        # Para montar una app Flask en Gradio se necesita gr.mount_gradio_app
        # Pero esto lo haríamos si Gradio fuera el frontend principal.
        # En nuestro caso, queremos el HTML/JS como frontend.

        # La solución de servir el index.html directamente desde Flask en la ruta "/"
        # y con sdk:python es la más limpia.

        # Volvemos a la idea de que Flask sirva el index.html.
        # El error "This Space is missing an app file" sugiere que Gradio no vio su UI.

        # Si el sdk es gradio, el app.py debe contener una interfaz de Gradio.
        # Si queremos Flask, el sdk debe ser Dockerfile o Python y nuestro app.py ser el entrypoint.

        # Revisado: el `sdk: gradio` espera que el `app.py` cree un `gr.Interface` o `gr.Blocks`
        # y lo llame `.launch()`.

        # Por lo tanto, necesitamos que este `app.py` sea una interfaz de Gradio
        # y que esa interfaz de Gradio INCLUYA nuestro frontend HTML y nuestro backend API.

        # Para servir un frontend HTML estático y un backend Flask en el mismo Space con sdk:gradio
        # la forma más sencilla es usar gr.File para el frontend y gr.API para el backend.
        # O, más directo, que Gradio se convierta en un proxy para nuestro Flask.

        # Opción: Simplemente hacer una app.py de Gradio que muestre un iframe.
        # Esto es lo que Hugging Face Spaces espera si el SDK es Gradio.

        gr.HTML(value="""
            <iframe src="/" style="width: 100%; height: 100vh; border: none;"></iframe>
        """)
        # La URL principal "/" será servida por nuestra aplicación Flask.
        # Esto es un truco para que Gradio "contenga" nuestra app Flask/HTML.
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
