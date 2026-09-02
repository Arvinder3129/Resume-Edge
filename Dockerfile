FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose Cloud Run port
ENV PORT=8080

# Start with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]
