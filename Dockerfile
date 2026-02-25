FROM python:3.10-slim

WORKDIR /app

# Copiar dependencias primero (para caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Puerto que usa HF Spaces (DEBE ser 7860)
EXPOSE 7860

# Arrancar Flask en el puerto correcto
CMD ["python", "app.py"]
