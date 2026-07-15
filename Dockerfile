FROM python:3.10-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and directories
COPY app/ ./app/
COPY utils/ ./utils/
COPY prompts/ ./prompts/
COPY templates/ ./templates/
COPY static/ ./static/
COPY main.py .

# Create docs and chroma_db directory mounts inside container
RUN mkdir -p docs chroma_db

# Expose port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
