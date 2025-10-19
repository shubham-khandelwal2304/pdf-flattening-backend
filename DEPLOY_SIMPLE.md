# Simple Render Deployment Guide

## Step-by-Step Deployment (Without render.yaml)

### 1. **Prepare Your Files**
Make sure you have these files in the `backend` folder:
- `app.py` ✅
- `requirements.txt` ✅
- `Procfile` ✅
- `runtime.txt` ✅

### 2. **Deploy on Render**
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. **Important Settings:**
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

### 3. **Environment Variables (Optional)**
In Render dashboard, add:
- `PYTHON_VERSION`: `3.11.0`

### 4. **Deploy**
Click "Create Web Service" and wait for deployment.

## Common Issues & Solutions

### Issue: "Build failed"
**Solution:**
- Check that all files are in the `backend` folder
- Ensure `requirements.txt` has no syntax errors
- Verify Python version compatibility

### Issue: "Service failed to start"
**Solution:**
- Check Procfile format (no extra spaces)
- Ensure gunicorn is in requirements.txt
- Check app.py imports

### Issue: "Module not found"
**Solution:**
- PyMuPDF might need system dependencies
- Try adding to requirements.txt:
  ```
  PyMuPDF==1.23.14
  Flask==2.3.3
  Flask-CORS==4.0.0
  Werkzeug==2.3.7
  gunicorn==21.2.0
  ```

## Test Your Deployment

After deployment, test these URLs:
- `https://your-app.onrender.com/` - Should show API info
- `https://your-app.onrender.com/api/ocr-tips` - Should show tips

## If Still Failing

**Tell me the exact error message** from the Render logs, and I'll help you fix it!
