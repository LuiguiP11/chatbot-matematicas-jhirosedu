FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

<<<<<<< HEAD
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "120", "app:app"]
=======
CMD ["python", "app.py"]
>>>>>>> 332066252669828247441d7ccc198a2da2c22e19
