# Render Deployment Troubleshooting Guide

## Common Render Deployment Issues and Solutions

### 1. **Build Failures**

#### Issue: "Module not found" errors
**Solution:**
- Ensure all dependencies are in `requirements.txt`
- Check that PyMuPDF is properly specified
- Try updating to latest versions

#### Issue: "Command not found" errors
**Solution:**
- Verify `Procfile` has correct format: `web: gunicorn app:app`
- No extra spaces or blank lines in Procfile
- Ensure gunicorn is in requirements.txt

### 2. **Runtime Errors**

#### Issue: "Port binding" errors
**Solution:**
- Use `gunicorn --bind 0.0.0.0:$PORT app:app` in Procfile
- Ensure app uses `os.environ.get('PORT', 5000)`

#### Issue: "Memory exceeded" errors
**Solution:**
- Upgrade to paid plan for more memory
- Optimize PDF processing for smaller files
- Add memory monitoring

### 3. **File Upload Issues**

#### Issue: "File too large" errors
**Solution:**
- Reduce MAX_FILE_SIZE in app.py
- Implement file size validation
- Add progress indicators for large files

### 4. **CORS Issues**

#### Issue: Frontend can't connect to backend
**Solution:**
- Ensure Flask-CORS is installed
- Add CORS configuration: `CORS(app)`
- Check frontend API URL configuration

## Step-by-Step Deployment

### 1. **Prepare Repository**
```bash
# Ensure backend folder structure:
backend/
├── app.py
├── requirements.txt
├── Procfile
├── runtime.txt
└── render.yaml
```

### 2. **Deploy on Render**
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Set **Root Directory** to `backend`
5. Set **Build Command** to `pip install -r requirements.txt`
6. Set **Start Command** to `gunicorn --bind 0.0.0.0:$PORT app:app`
7. Click "Create Web Service"

### 3. **Environment Variables**
Add these in Render dashboard:
- `PYTHON_VERSION`: `3.11.0`
- `PORT`: `10000` (optional, Render sets this automatically)

### 4. **Monitor Deployment**
- Check build logs for errors
- Monitor runtime logs
- Test API endpoints

## Alternative Deployment Commands

### If gunicorn fails, try:
```bash
# In Procfile:
web: python app.py
```

### If port issues persist:
```bash
# In Procfile:
web: gunicorn --bind 0.0.0.0:$PORT --workers 1 app:app
```

## Testing Your Deployment

### 1. **Check API Status**
```bash
curl https://your-app.onrender.com/
```

### 2. **Test Upload Endpoint**
```bash
curl -X POST https://your-app.onrender.com/api/upload
```

### 3. **Check OCR Tips**
```bash
curl https://your-app.onrender.com/api/ocr-tips
```

## Common Error Messages

### "Build failed"
- Check requirements.txt syntax
- Verify Python version compatibility
- Check for missing dependencies

### "Service failed to start"
- Check Procfile format
- Verify gunicorn installation
- Check port binding configuration

### "Module import error"
- Ensure all imports are available
- Check PyMuPDF installation
- Verify Flask and dependencies

## Getting Help

1. **Check Render Logs**: Go to your service dashboard → Logs
2. **Test Locally**: Run `python app.py` locally first
3. **Check Dependencies**: Ensure all packages install correctly
4. **Contact Support**: Use Render's support if issues persist

## Success Indicators

✅ Build completes without errors
✅ Service starts successfully
✅ API responds to requests
✅ File upload works
✅ PDF processing completes
✅ Download functionality works
