# 🔧 CD Pipeline Troubleshooting Guide

## Quick Fixes

### Issue: "This workflow does not exist"

**Possible Causes:**
1. Workflow file not on the default branch (master)
2. GitHub Actions not enabled
3. Workflow file has syntax errors
4. File not committed/pushed

**Solutions:**

#### 1. Verify File Exists on GitHub
```
https://github.com/curiaz/medichain/tree/master/.github/workflows
```
You should see:
- ✅ `cd-production.yml`
- ✅ `cd-staging.yml`

#### 2. Check GitHub Actions Settings
- Go to: **Settings → Actions → General**
- Ensure "Allow all actions and reusable workflows" is selected
- Check "Workflow permissions" → "Read and write permissions"

#### 3. Push Workflow Files
```bash
git checkout master
git add .github/workflows/cd-production.yml
git commit -m "Add CD production workflow"
git push origin master
```

#### 4. Wait a Few Minutes
GitHub sometimes takes 1-2 minutes to recognize new workflows.

---

### Issue: CD Workflow Not Visible in Sidebar

**This is NORMAL!** Workflows only appear in the sidebar after they run at least once.

**Solution:**
1. Go to: `https://github.com/curiaz/medichain/actions/workflows/cd-production.yml`
2. Click **"Run workflow"** button
3. Select branch: `master`
4. Click **"Run workflow"**
5. After it runs, it will appear in the sidebar!

---

### Issue: CD Not Triggering Automatically

**Check These:**

1. **CI Must Pass First**
   - CD only triggers after CI passes
   - Check: Actions → CI/CD Pipeline → Latest run = ✅

2. **Correct Branch**
   - Production CD: Only triggers on `master`
   - Staging CD: Only triggers on `develop`

3. **Workflow Name Match**
   - CD looks for: `"CI/CD Pipeline"`
   - CI workflow name must be exactly: `CI/CD Pipeline`
   - Check: `.github/workflows/ci.yml` → `name: CI/CD Pipeline`

4. **Permissions**
   - Settings → Actions → General → Workflow permissions
   - Must be "Read and write permissions"

---

### Issue: Manual Trigger Not Working

**Try These:**

1. **Direct URL Method:**
   ```
   https://github.com/curiaz/medichain/actions/workflows/cd-production.yml
   ```
   Click "Run workflow" button

2. **Via Actions Tab:**
   - Go to Actions → All workflows
   - Search for "cd-production"
   - Click on it → "Run workflow"

3. **Check Branch:**
   - Make sure you're trying to run on `master` branch
   - The workflow is configured for `master` only

---

### Issue: Workflow Runs But Fails

**Common Errors:**

#### Error: "Firebase service account not found"
- **Fix:** Add secret `FIREBASE_SERVICE_ACCOUNT_MEDICHAIN_8773B`
- **Location:** Settings → Secrets and variables → Actions

#### Error: "Environment not found"
- **Fix:** Create environments in Settings → Environments
- **Names needed:** `production`, `staging`, `production-backend`, `staging-backend`
- Or remove `environment:` lines from workflow (optional)

#### Error: "Build failed"
- Check build logs
- Verify `package.json` exists
- Check Node.js version matches (workflow uses Node 18)

---

## Step-by-Step Debugging

### Step 1: Verify Files Are on GitHub
```bash
# Check if files exist
curl https://api.github.com/repos/curiaz/medichain/contents/.github/workflows/cd-production.yml
```

### Step 2: Test Simple Workflow First
I created `test-cd-simple.yml` - push it and test:
```bash
git add .github/workflows/test-cd-simple.yml
git commit -m "Add test CD workflow"
git push origin master
```
Then go to Actions and look for "Test CD - Simple"

### Step 3: Check Workflow Syntax
The workflow uses YAML - verify no syntax errors:
- Proper indentation (spaces, not tabs)
- Correct YAML structure
- All quotes properly closed

### Step 4: Test Manual Trigger
1. Go to workflow URL directly
2. Click "Run workflow"
3. Watch it run
4. Check logs for errors

---

## Nuclear Option: Simplify the Workflow

If nothing works, we can create a super simple version:

```yaml
name: CD - Simple Test

on:
  workflow_dispatch:
  push:
    branches: [master]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Test
        run: echo "CD is working!"
```

This will at least verify GitHub Actions can see and run your workflows.

---

## Still Not Working?

**Check These GitHub Settings:**

1. **Repository Settings → Actions → General**
   - ✅ Actions permissions: "Allow all actions"
   - ✅ Workflow permissions: "Read and write"
   - ✅ Allow GitHub Actions to create and approve pull requests: Enabled

2. **Repository Settings → Actions → Runners**
   - Should show "GitHub-hosted runners" available

3. **Account/Organization Settings**
   - If organization: Check organization Actions settings
   - Verify billing (even if you said not to worry, sometimes it blocks things)

---

## Quick Test Checklist

- [ ] Workflow file exists on GitHub (check URL)
- [ ] File is on `master` branch
- [ ] GitHub Actions is enabled
- [ ] Workflow permissions are correct
- [ ] Can access workflow via direct URL
- [ ] Manual trigger button appears
- [ ] Workflow runs when triggered
- [ ] Check logs for specific errors

---

**Need More Help?** Share the specific error message or what happens when you try to trigger it!

