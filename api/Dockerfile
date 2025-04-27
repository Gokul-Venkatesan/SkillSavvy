# Use Debian-based image that supports apt
FROM python:3.10-bullseye

# Set working directory
WORKDIR /app

# Install Tesseract and dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    poppler-utils \
    imagemagick \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Print tesseract path and version (debugging)
RUN echo "Tesseract path: $(which tesseract)" && tesseract --version

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optional: download spaCy model if used
RUN python -m spacy download en_core_web_sm

# Copy all your FastAPI app files into the container
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Launch FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
