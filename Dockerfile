FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD exec gunicorn \
    --bind :$PORT \
    --workers 1 \
    --threads 8 \
    --timeout 300 \
    main:app
