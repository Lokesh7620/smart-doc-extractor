#!/bin/bash
# Render.com Build Script
# Install system dependencies and Python packages

echo "=== Starting Render.com Build ==="

# Update package lists
echo "Updating package lists..."
apt-get update -y

# Install Tesseract OCR
echo "Installing Tesseract OCR..."
apt-get install -y tesseract-ocr tesseract-ocr-eng

# Install Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.render.txt

echo "=== Build Complete ==="
