@echo off
echo === Merging Dashboard Branch to Master ===
echo.

echo Step 1: Checking current branch...
git branch --show-current
echo.

echo Step 2: Stashing any uncommitted changes...
git stash push -m "Stash before merging dashboard to master"
echo.

echo Step 3: Switching to master branch...
git checkout master
if errorlevel 1 (
    echo ERROR: Failed to switch to master branch
    pause
    exit /b 1
)
echo.

echo Step 4: Pulling latest changes from remote...
git pull origin master
echo.

echo Step 5: Merging dashboard branch...
git merge dashboard --no-ff -m "Merge dashboard branch: Admin board UI improvements and enhancements"
if errorlevel 1 (
    echo ERROR: Merge failed. Please resolve conflicts manually.
    pause
    exit /b 1
)
echo.

echo === Merge Successful ===
echo Dashboard branch has been merged into master.
echo.
echo Next steps:
echo 1. Review the merge
echo 2. Push to remote: git push origin master
echo 3. Update failing tests (13 tests need updates due to UI restructuring)
echo.
pause

