# Merge Dashboard Branch to Master
# This script performs the merge operation

Write-Host "=== Merging Dashboard Branch to Master ===" -ForegroundColor Cyan

# Check current branch
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch" -ForegroundColor Yellow

# Check if there are uncommitted changes
$status = git status --porcelain
if ($status) {
    Write-Host "Warning: There are uncommitted changes. Stashing them..." -ForegroundColor Yellow
    git stash push -m "Stash before merging dashboard to master"
}

# Switch to master branch
Write-Host "`nSwitching to master branch..." -ForegroundColor Cyan
git checkout master
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to switch to master branch" -ForegroundColor Red
    exit 1
}

# Pull latest changes from remote
Write-Host "Pulling latest changes from origin/master..." -ForegroundColor Cyan
git pull origin master
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Failed to pull from remote. Continuing anyway..." -ForegroundColor Yellow
}

# Merge dashboard branch
Write-Host "`nMerging dashboard branch into master..." -ForegroundColor Cyan
git merge dashboard --no-ff -m "Merge dashboard branch: Admin board UI improvements and enhancements"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Merge failed. Please resolve conflicts manually." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Merge Successful ===" -ForegroundColor Green
Write-Host "Dashboard branch has been merged into master." -ForegroundColor Green

# Show merge summary
Write-Host "`nMerge Summary:" -ForegroundColor Cyan
git log --oneline -1

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Review the merge" -ForegroundColor White
Write-Host "2. Push to remote: git push origin master" -ForegroundColor White
Write-Host "3. Update failing tests (13 tests need updates due to UI restructuring)" -ForegroundColor White

