---
title: Taby Tutora de Matemática
emoji: 📚
colorFrom: green
colorTo: blue
sdk: python
app_file: app.py
# La sección "models" es para indicar qué modelos se usarán, pero no es estrictamente necesaria si se definen en el app.py
# models:
#   - mistralai/Mixtral-8x7B-Instruct-v0.1

# Esto es para configurar que los archivos estáticos se sirvan desde la raíz,
# y que cualquier ruta no encontrada se redirija a index.html (para SPAs o frontends)
# build:
#   python_version: 3.10
#   install: pip install -r requirements.txt
#   command: python app.py
#
# ports:
#   - 7860 # Puerto por defecto de Gradio, pero si usamos Flask se puede cambiar a 5000 o el que use Flask.

# Para Flask, el command generalmente es gunicorn o flask run
# Dado que es Flask, y Hugging Face espera que la app se sirva en un puerto específico
# y que el frontend esté en el mismo Space, la configuración más simple
# es un Dockerfile, pero si queremos usar el sdk:python
# necesitamos una forma de servir Flask y el static folder.

# La forma más robusta y que sirve Python con frontend estático
# es usando un Dockerfile. Sin embargo, si queremos mantenerlo simple con sdk:python,
# necesitamos que el app.py sirva tanto la API como el index.html.

# Dado que Hugging Face Spaces usa el `app.py` para la lógica del backend,
# y queremos que sirva el `index.html` estático, la forma más sencilla es:
# 1. Decirle que el SDK es Python.
# 2. Asegurarnos de que el app.py sirva los archivos estáticos (index.html).
#    Esto es algo que hay que añadir al app.py
# 3. Y que el comando de ejecución sea el de Flask.

# Para una app de Flask que sirve archivos estáticos junto con una API:
# Necesitamos un Dockerfile o modificar el app.py para servir index.html
# Ya que el sdk es Python, Hugging Face Spaces espera un app.py que se ejecute.
# y si queremos servir archivos estáticos, el `app.py` debe manejarlo.

# Revisado: la configuración ideal para que el app.py de Flask sirva los archivos estáticos
# y la API en el mismo Space es cambiar la configuración del SDK y asegurar que Flask
# sirva el index.html.

# Para este caso, vamos a usar sdk: gradio porque es el más sencillo de configurar
# para servir archivos estáticos (nuestro index.html) y a la vez tener un backend de Python.
# Luego, nuestro app.py será el que se ejecute detrás.
sdk: gradio
app_file: app.py
output_dir: .
---

# chatbot-matematicas-jhirosedu
Chatbot de Matemáticas para Jhiro's Edu, enfocado en el CNB
