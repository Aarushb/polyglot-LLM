# Build and Test Script for Polyglot-LLM

Write-Host "=== Polyglot-LLM Build Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if SCons is installed
Write-Host "Checking for SCons..." -ForegroundColor Yellow
try {
    $sconsVersion = scons --version 2>&1 | Select-String "SCons" | Out-String
    if ($sconsVersion) {
        Write-Host "✓ SCons found" -ForegroundColor Green
        Write-Host $sconsVersion.Trim()
    }
} catch {
    Write-Host "✗ SCons not found" -ForegroundColor Red
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
scons

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
