# Use a specific Python 3.10 Debian image
FROM python:3.10-bullseye

# Set the working directory
WORKDIR /app

# Install system packages (including Tesseract)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    imagemagick \
    libleptonica-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies first and install them
COPY ./api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Optional: Install spaCy model
RUN python -m spacy download en_core_web_sm

# Copy app code
COPY ./api /app

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
