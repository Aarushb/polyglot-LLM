# Build and Test Script for Polyglot-LLM

Write-Host "=== Polyglot-LLM Build Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a virtual environment
$inVenv = $env:VIRTUAL_ENV -ne $null
if ($inVenv) {
    Write-Host "✓ Virtual environment detected: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "⚠ Not in virtual environment - using system Python" -ForegroundColor Yellow
}

# Check if SCons is installed
Write-Host ""
Write-Host "Checking for build dependencies..." -ForegroundColor Yellow

try {
    $pythonCmd = if ($inVenv) { "python" } else { "python" }
    & $pythonCmd -c "import SCons; import markdown" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Build dependencies found" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Build dependencies not found" -ForegroundColor Red
    Write-Host "Installing build dependencies..." -ForegroundColor Yellow
    pip install -r requirements-build.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Build dependencies installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Building addon..." -ForegroundColor Yellow

# Use python -m SCons for better compatibility
& $pythonCmd -m SCons

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Build successful!" -ForegroundColor Green
    Write-Host ""
    
    # Find the built addon file
    $addonFile = Get-ChildItem -Filter "*.nvda-addon" | Select-Object -First 1
    
    if ($addonFile) {
        Write-Host "Addon file created:" -ForegroundColor Cyan
        Write-Host "  Name: $($addonFile.Name)" -ForegroundColor White
        Write-Host "  Size: $([math]::Round($addonFile.Length / 1KB, 2)) KB" -ForegroundColor White
        Write-Host "  Path: $($addonFile.FullName)" -ForegroundColor White
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "  1. Double-click the .nvda-addon file to install" -ForegroundColor White
        Write-Host "  2. Restart NVDA when prompted" -ForegroundColor White
        Write-Host "  3. Configure in NVDA → Preferences → Settings → Polyglot-LLM" -ForegroundColor White
        Write-Host "  4. See STATUS.md for testing checklist" -ForegroundColor White
    } else {
        Write-Host "✗ Warning: .nvda-addon file not found" -ForegroundColor Red
    }
} else {
    Write-Host "✗ Build failed - check errors above" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Build Complete ===" -ForegroundColor Cyan
