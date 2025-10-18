# PDF Flattener Backend

This is the backend API for the PDF Flattener web application, designed to be deployed on Render.

## Features

- 🔧 Flask-based REST API
- 📄 PDF flattening with OCR optimization
- ⚡ Real-time processing status updates
- 🎯 Configurable DPI settings (400-2400)
- 🔍 Maximum OCR quality mode
- 📦 Smart compression while preserving quality
- 🧹 Automatic file cleanup
- 🔒 CORS support for frontend integration

## API Endpoints

- `GET /` - API information and status
- `POST /api/upload` - Upload and process PDF file
- `GET /api/status/<task_id>` - Get processing status
- `GET /api/download/<task_id>` - Download processed file
- `DELETE /api/cleanup/<task_id>` - Clean up processed files
- `GET /api/ocr-tips` - Get OCR optimization tips

## Deployment on Render

### Option 1: Deploy via Render Dashboard

1. Go to [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set the following configuration:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3.11
   - **Root Directory**: `backend`

### Option 2: Deploy via Render CLI

1. Install Render CLI:
   ```bash
   npm install -g @render/cli
   ```

2. Login to Render:
   ```bash
   render login
   ```

3. Deploy:
   ```bash
   render deploy
   ```

### Option 3: Deploy via GitHub Integration

1. Push your code to GitHub
2. Connect your GitHub repository to Render
3. Set the root directory to `backend`
4. Deploy automatically on every push

## Environment Variables

The following environment variables are automatically set by Render:

- `PORT` - Port number (automatically set by Render)
- `PYTHON_VERSION` - Python version (set to 3.11.0)

## Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The API will be available at `http://localhost:5000`

## File Structure

```
backend/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile           # Process configuration for Render
├── render.yaml        # Render deployment configuration
└── README.md          # This file
```

## API Usage

### Upload a PDF

```bash
curl -X POST -F "file=@document.pdf" -F "dpi=600" -F "max_ocr_quality=false" https://your-app.onrender.com/api/upload
```

### Check Status

```bash
curl https://your-app.onrender.com/api/status/<task_id>
```

### Download Result

```bash
curl -O https://your-app.onrender.com/api/download/<task_id>
```

## Configuration

The backend supports the following parameters:

- **dpi**: DPI setting (400-2400, default: 600)
- **max_ocr_quality**: Enable maximum OCR quality mode (true/false, default: false)

## Performance

- **Processing Speed**: Optimized for speed with quality preservation
- **Memory Usage**: Efficient memory management for large files
- **File Size**: Smart compression maintains quality under 20MB when possible
- **Concurrent Processing**: Handles multiple files simultaneously

## Security

- File type validation (PDF only)
- Secure filename handling
- Automatic file cleanup
- Size limits and validation
- CORS protection for frontend integration

## Monitoring

Render provides built-in monitoring and logging for your deployed application. Check the Render dashboard for:

- Application logs
- Performance metrics
- Error tracking
- Resource usage

## Troubleshooting

### Common Issues

1. **Build Failures**: Ensure all dependencies are in `requirements.txt`
2. **Memory Issues**: For large files, consider upgrading to a paid plan
3. **Timeout Issues**: Large files may take longer to process

### Getting Help

- Check the Render dashboard logs
- Review the application logs for detailed error messages
- Ensure all dependencies are properly installed

## License

This project is open source and available under the MIT License.

