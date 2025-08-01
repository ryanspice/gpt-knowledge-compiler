# PowerShell script to add Tesseract OCR to PATH

# Tesseract installation path
$tesseractPath = "C:\Program Files\Tesseract-OCR"

# Function to add Tesseract to system PATH
Function Add-TesseractToPath {
    $systemPath = [System.Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::Machine)

    if (-not $systemPath.Contains($tesseractPath)) {
        $newPath = $systemPath + ";" + $tesseractPath
        [System.Environment]::SetEnvironmentVariable("PATH", $newPath, [System.EnvironmentVariableTarget]::Machine)
        Write-Host "Tesseract OCR path added to system PATH."
    } else {
        Write-Host "Tesseract OCR path is already in system PATH."
    }
}

# Check if Tesseract OCR directory exists
if (Test-Path -Path $tesseractPath) {
    Add-TesseractToPath
} else {
    Write-Host "Tesseract OCR directory not found at $tesseractPath. Please install Tesseract OCR or check the installation path."
}

# Refresh environment variables for the current session
$env:Path = [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
