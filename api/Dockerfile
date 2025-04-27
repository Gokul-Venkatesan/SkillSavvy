FROM python:3.10-slim

# Set working directory to the api folder
WORKDIR /app

# Install Tesseract and dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN tesseract --version

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirem

# Copy only the api folder contents
COPY . .

# Expose port (optional, needed if using something like Flask or FastAPI)
EXPOSE 8000

# Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
