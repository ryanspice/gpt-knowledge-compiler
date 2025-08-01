#!/bin/bash
# Check for Tesseract OCR
Function Check-Tesseract {
    $tesseract = Get-Command "tesseract" -ErrorAction SilentlyContinue
    if ($tesseract) {
        Write-Host "Tesseract OCR is already installed."
    } else {
        install_tesseract();
    }
}

# Check for Python and Install Packages
if (-Not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "Python could not be found. Please install Python first."
    exit
} else {
    Write-Host "Installing required Python packages..."
    pip install pytesseract pdf2image py7zr markdown2 python-docx pyyaml tqdm pillow
    Check-Tesseract
    Write-Host "Installation completed."
}

# Function to install Tesseract OCR
install_tesseract() {
    echo "Installing Tesseract OCR..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install tesseract-ocr -y
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew update
        brew install tesseract
    elif [[ "$OSTYPE" == "msys"* ]]; then
        # Windows (Git Bash)
        echo "Please install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki and add it to your PATH"
    else
        echo "Unknown Operating System. Tesseract OCR installation needs to be done manually."
    fi
}