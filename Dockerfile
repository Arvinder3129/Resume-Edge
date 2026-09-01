# Use official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy all files into container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Cloud Run port
ENV PORT=8080
EXPOSE 8080

# Start Flask app
CMD ["python", "main.py"]
