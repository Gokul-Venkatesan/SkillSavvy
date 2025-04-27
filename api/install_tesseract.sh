#!/bin/bash
set -e

# Update package list and install Tesseract and required libraries
apt-get update
apt-get install -y tesseract-ocr

# Install any additional language packs if needed (optional)
apt-get install -y tesseract-ocr-eng tesseract-ocr-spa  # English, Spanish example
