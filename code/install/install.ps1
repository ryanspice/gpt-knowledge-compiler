# Check for Tesseract OCR
Function Check-Tesseract {
    $tesseract = Get-Command "tesseract" -ErrorAction SilentlyContinue
    if ($tesseract) {
        Write-Host "Tesseract OCR is already installed."
    } else {
        Write-Host "Tesseract OCR is not installed. Please install it from https://github.com/UB-Mannheim/tesseract/wiki"
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
