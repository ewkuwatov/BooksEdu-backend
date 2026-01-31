FROM python:3.12-slim

# Устанавливаем системные зависимости, необходимые для bcrypt
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libffi-dev python3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
