# Auto Deploy to Render.com - PowerShell Script
# This script automates as much as possible for Render deployment

Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "AUTOMATED RENDER.COM DEPLOYMENT" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Step 1: Check GitHub CLI
Write-Host "`n[1/6] Checking GitHub CLI..." -ForegroundColor Yellow
$ghInstalled = $null -ne (Get-Command gh -ErrorAction SilentlyContinue)

if (-not $ghInstalled) {
    Write-Host "  GitHub CLI not found. Installing..." -ForegroundColor Yellow
    Write-Host "`n  Installing GitHub CLI via winget..." -ForegroundColor Cyan
    winget install --id GitHub.cli --silent
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Host "  Please restart this script after installation completes.`n" -ForegroundColor Red
    Write-Host "  Then run: .\auto_deploy_render_fixed.ps1" -ForegroundColor Yellow
    exit
}

Write-Host "  OK GitHub CLI installed" -ForegroundColor Green

# Step 2: GitHub Authentication
Write-Host "`n[2/6] Checking GitHub authentication..." -ForegroundColor Yellow
$ghAuth = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Not logged in. Opening GitHub authentication..." -ForegroundColor Yellow
    gh auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  GitHub authentication failed" -ForegroundColor Red
        exit 1
    }
}
Write-Host "  OK GitHub authenticated" -ForegroundColor Green

# Step 3: Create GitHub Repository
Write-Host "`n[3/6] Creating GitHub repository..." -ForegroundColor Yellow
$repoName = "smart-doc-extractor"

# Check if repo already exists
$repoExists = gh repo view $repoName 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Repository already exists: $repoName" -ForegroundColor Yellow
    $response = Read-Host "  Use existing repo? (y/n)"
    if ($response -ne "y") {
        $repoName = Read-Host "  Enter new repository name"
    }
}
else {
    Write-Host "  Creating new repository: $repoName" -ForegroundColor Cyan
    gh repo create $repoName --public --source=. --remote=origin --description="Smart Document Extractor with OCR and Translation"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Failed to create repository" -ForegroundColor Red
        exit 1
    }
    Write-Host "  Repository created" -ForegroundColor Green
}

# Step 4: Push to GitHub
Write-Host "`n[4/6] Pushing code to GitHub..." -ForegroundColor Yellow
git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Failed to push to GitHub" -ForegroundColor Red
    exit 1
}
Write-Host "  OK Code pushed successfully" -ForegroundColor Green

# Step 5: Get GitHub repository URL
$username = gh api user --jq .login
$repoUrl = "https://github.com/$username/$repoName"
Write-Host "`n  GitHub Repository: $repoUrl" -ForegroundColor Cyan

# Step 6: Open Render.com
Write-Host "`n[5/6] Opening Render.com..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process "https://dashboard.render.com/select-repo?type=blueprint"

Write-Host "  OK Render.com opened in browser" -ForegroundColor Green

# Final Instructions
Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "OK AUTOMATED SETUP COMPLETE!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan

Write-Host "`nYour code is now on GitHub:" -ForegroundColor Yellow
Write-Host "  $repoUrl" -ForegroundColor Cyan

Write-Host "`n" -NoNewline
Write-Host "NEXT: Complete deployment on Render.com" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan

Write-Host "`nIn the browser window that just opened:" -ForegroundColor White
Write-Host "  1. Click Connect next to GitHub" -ForegroundColor White
Write-Host "  2. Select repository: $repoName" -ForegroundColor Cyan
Write-Host "  3. Click Apply to deploy with render.yaml" -ForegroundColor White
Write-Host "  4. Wait 10-12 minutes for deployment" -ForegroundColor White
Write-Host "  5. Your app will be live at: https://smart-doc-extractor.onrender.com" -ForegroundColor Green

Write-Host "`nALTERNATIVE: Manual Blueprint Deployment" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  1. Go to: https://dashboard.render.com" -ForegroundColor White
Write-Host "  2. Click New + then Blueprint" -ForegroundColor White
Write-Host "  3. Select your repo: $repoName" -ForegroundColor Cyan
Write-Host "  4. Render will auto-detect render.yaml" -ForegroundColor White
Write-Host "  5. Click Apply button" -ForegroundColor White

Write-Host "`n" -NoNewline
Write-Host "DEPLOYMENT DETAILS" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Database: PostgreSQL (free tier)" -ForegroundColor White
Write-Host "  SSL: Included (automatic https://)" -ForegroundColor White
Write-Host "  Deploy time: 10-12 minutes" -ForegroundColor White
Write-Host "  Free tier: 750 hours/month" -ForegroundColor White
Write-Host "  URL: https://smart-doc-extractor.onrender.com" -ForegroundColor Green

Write-Host "`n" -NoNewline
Write-Host "MONITORING" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  After deployment starts, you can:" -ForegroundColor White
Write-Host "  - View build logs in Render dashboard" -ForegroundColor White
Write-Host "  - Check deployment status" -ForegroundColor White
Write-Host "  - Access your live app URL" -ForegroundColor White

Write-Host "`n" -NoNewline
Write-Host "Press any key to open Render dashboard..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Start-Process "https://dashboard.render.com"

Write-Host "`n" -NoNewline
Write-Host "Done! Follow the steps above to complete deployment." -ForegroundColor Green
Write-Host ""
