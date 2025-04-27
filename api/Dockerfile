# Use a slim Python image
FROM python:3.9-slim

# Install Tesseract and system dependencies
RUN apt-get update && apt-get install -y tesseract-ocr

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
# COPY . .

# Download the spaCy model
RUN python -m spacy download en_core_web_sm

# Expose the app's port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
