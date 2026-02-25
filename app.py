from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import PyPDF2

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def cargar_cnb(ruta_pdf="cnb_matematicas.pdf"):
    texto = ""
    try:
        with open(ruta_pdf, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for pagina in reader.pages:
                texto += pagina.extract_text() + "\n"
        print("CNB cargado correctamente.")
    except Exception as e:
        print(f"Advertencia: No se pudo cargar el CNB: {e}")
        texto = ""
    return texto

CNB_TEXTO = cargar_cnb()

SYSTEM_PROMPT = """
Eres "Taby Tutora de Matemática", un asistente educativo amigable, 
paciente y motivador para estudiantes de 1º, 2º y 3º básico del 
Instituto Experimental de Educación Básica con Orientación Ocupacional (Guatemala).

REGLAS ESTRICTAS:
1. Solo respondes preguntas de matemáticas del CNB de 1º a 3º básico.
2. NUNCA des respuestas directas a tareas o exámenes. Guía paso a paso.
3. Usa lenguaje sencillo y ejemplos con contexto guatemalteco.
4. Máximo 3-4 párrafos por respuesta.
5. Sé respetuoso y positivo en todo momento.
"""

def buscar_contexto_cnb(pregunta, max_chars=1500):
    if not CNB_TEXTO:
        return ""
    palabras = pregunta.lower().split()
    parrafos = CNB_TEXTO.split("\n\n")
    relevantes = []
    for parrafo in parrafos:
        if len(parrafo.strip()) < 20:
            continue
        score = sum(1 for p in palabras if p in parrafo.lower())
        if score > 0:
            relevantes.append((score, parrafo))
    relevantes.sort(reverse=True)
    contexto = "\n\n".join([p for _, p in relevantes[:3]])
    return contexto[:max_chars]

@app.route("/")
def home():
    return send_from_directory('.', 'index.html', mimetype='text/html')

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route("/chat", methods=["POST"])
def chat():
    if not GROQ_API_KEY:
        return jsonify({"error": "GROQ_API_KEY no configurada."}), 500

    data = request.get_json()
    user_message = data.get("message", "")
    conversation_history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400

    contexto_cnb = buscar_contexto_cnb(user_message)
    system_content = SYSTEM_PROMPT
    if contexto_cnb:
        system_content += f"\n\nCONTEXTO DEL CNB RELEVANTE:\n{contexto_cnb}"

    messages = [{"role": "system", "content": system_content}]
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
            "temperature": 0.7
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        bot_text = response.json()["choices"][0]["message"]["content"]
        return jsonify({"response": bot_text})

    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)