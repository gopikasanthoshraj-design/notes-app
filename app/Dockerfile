# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose the port Cloud Run expects
EXPOSE 8080

# Environment variables (optional, mostly for local dev)
ENV FLASK_APP=app.py

# Start the app
CMD ["python", "app.py"]