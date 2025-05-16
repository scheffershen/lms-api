FROM python:3.12-slim

# Set working directory to a temp location for installing requirements
WORKDIR /tmp

# Copy and install requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the actual working directory to /app/bonus/api
WORKDIR /app/bonus/api

# Copy the application code
COPY . .

EXPOSE 8000

# Add the parent directory to PYTHONPATH and run uvicorn
CMD ["sh", "-c", "PYTHONPATH=/app/bonus/api uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"] 