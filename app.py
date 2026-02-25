from flask import Flask, render_template, request, jsonify
from groq import Groq
import os
import PyPDF2 # Nueva importación para leer PDFs

app = Flask(__name__, template_folder='templates', static_folder='static')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- Parte de la integración del CNB (RAG simplificado) ---
def cargar_cnb(ruta_pdf="cnb_matematicas.pdf"):
    texto = ""
    try:
        with open(ruta_pdf, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for pagina in reader.pages:
                texto += pagina.extract_text() + "\n"
        print(f"CNB cargado exitosamente desde {ruta_pdf}")
    except FileNotFoundError:
        print(f"ERROR: Archivo CNB no encontrado en {ruta_pdf}")
        texto = "CNB no disponible. Por favor, asegúrate de que el archivo 'cnb_matematicas.pdf' esté en el directorio raíz del proyecto."
    except Exception as e:
        print(f"ERROR al cargar el CNB: {e}")
        texto = f"Error al cargar el CNB: {e}"
    return texto

# Cargar el CNB al iniciar la aplicación (una sola vez)
CNB_TEXTO = cargar_cnb()

def buscar_contexto(pregunta, texto_cnb, max_chars=2000):
    """Búsqueda simple: encuentra párrafos que contengan palabras clave"""
    if texto_cnb.startswith("ERROR"): # Si el CNB no se pudo cargar
        return texto_cnb # Devolvemos el mensaje de error

    palabras = pregunta.lower().split()
    parrafos = texto_cnb.split("\n\n")
    
    relevantes = []
    for parrafo in parrafos:
        score = sum(1 for p in palabras if p in parrafo.lower())
        if score > 0:
            relevantes.append((score, parrafo))
    
    relevantes.sort(reverse=True)
    # Limita a los 3 párrafos más relevantes para no exceder el contexto
    contexto = "\n\n".join([p for _, p in relevantes[:3]])
    return contexto[:max_chars] # Asegura que no exceda el límite de caracteres

# --- Fin Parte de la integración del CNB ---


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    conversation_history = data.get("history", []) # Recuperar el historial de la conversación
    #grado = data.get("grado", "1º básico")  # Se podría pasar desde el frontend si el usuario lo selecciona

    if not user_message:
        return jsonify({"error": "Mensaje de usuario vacío"}), 400

    # Búsqueda de contexto relevante del CNB
    contexto_cnb = buscar_contexto(user_message, CNB_TEXTO)

    # Construir el SYSTEM_PROMPT dinámicamente con el contexto del CNB
    system_prompt = f"""Eres Taby Tutora, tutora de matemáticas para estudiantes de básica en Guatemala.
                
CONTENIDO DEL CNB RELEVANTE:
{contexto_cnb}

Usa este contenido para guiar tus respuestas. Explica de forma simple y usa 
ejemplos del contexto guatemalteco (quetzales, mercados, etc.).
NUNCA des respuestas directas a tareas, ejercicios o exámenes; en cambio,
guías al estudiante paso a paso para que él encuentre la respuesta.
Sé respetuoso y positivo en todo momento.
"""

    # Construir el historial para GROQ (compatible con API de OpenAI)
    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history:
        # Asegurarse de que el historial solo contenga roles 'user' y 'assistant'
        if msg["role"] in ["user", "assistant"]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message}) # Añadir el mensaje actual del usuario

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # El modelo de GROQ
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        bot_text = response.choices[0].message.content
        return jsonify({"response": bot_text})

    except Exception as e:
        app.logger.error(f"Error al procesar la solicitud del chat: {e}")
        return jsonify({"error": f"Error al procesar la solicitud: {e}"}), 500

if __name__ == "__main__":
    # Puerto 7860 obligatorio para Hugging Face Spaces con Docker
    app.run(host="0.0.0.0", port=7860, debug=False)
