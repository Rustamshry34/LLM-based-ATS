# Dockerfile
FROM python:3.10-slim

# Kurulum öncesi temizlik
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Bağımlılıkları önce kopyala (cache avantajı)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodu kopyala
COPY . .

# Port aç
EXPOSE 8000

# Gunicorn ile başlat
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "api:app", "--bind", "0.0.0.0:8000"]


