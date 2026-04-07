FROM python:3.10-slim

WORKDIR /app

# Variable para forzar el refresco de caché en Hugging Face
ENV LAST_UPDATE=2026-04-06-22-10

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "120", "app:app"]
