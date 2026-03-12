# Render Build Fix - Python 3.11 Setup

## Problem
Render is using Python 3.13.4 by default, which is incompatible with pandas and scikit-learn.

## Solution: Update Build Command

In Render Dashboard → Settings → Build Command, use:

```bash
python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
```

## Alternative: Set Environment Variable

In Render Dashboard → Environment Variables, add:

- **Name:** `PYTHON_VERSION`
- **Value:** `3.11.9`

Then use this Build Command:
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

## Start Command (keep as is)
```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

