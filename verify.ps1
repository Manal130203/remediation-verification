$ErrorActionPreference = "Stop"

Write-Host "`n=== 1. Regression tests ===" -ForegroundColor Cyan
python -m unittest discover -s inputs -p "test_download.py" -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Regression tests FAILED." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== 2. Adversarial security tests ===" -ForegroundColor Cyan
python -m unittest discover -s inputs -p "test_adversarial.py" -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Adversarial tests FAILED." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== 3. Original vs fixed comparison ===" -ForegroundColor Cyan
python .\inputs\compare_versions.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Version comparison FAILED." -ForegroundColor Red
    exit 1
}

Write-Host "`nALL SECURITY CHECKS PASSED." -ForegroundColor Green
exit 0
