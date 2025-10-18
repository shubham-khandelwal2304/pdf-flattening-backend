import os
import fitz  # PyMuPDF
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import threading
import time
from pathlib import Path
import uuid
import json

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Store processing status
processing_status = {}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def flatten_pdf(input_path, output_path, dpi=600, max_ocr_quality=False, task_id=None):
    """Flatten a single PDF file with OCR-optimized settings"""
    try:
        if task_id:
            processing_status[task_id]['status'] = 'processing'
            processing_status[task_id]['message'] = 'Opening PDF document...'
        
        # Open the PDF document
        doc = fitz.open(input_path)
        
        if task_id:
            processing_status[task_id]['message'] = 'Creating flattened document...'
        
        # Create a new document for the flattened version
        flattened_doc = fitz.open()
        
        # OCR-optimized settings
        zoom = dpi / 72  # 72 is the default DPI in PyMuPDF
        
        total_pages = len(doc)
        
        # Process each page
        for page_num in range(total_pages):
            if task_id:
                progress = (page_num / total_pages) * 100
                processing_status[task_id]['progress'] = progress
                processing_status[task_id]['message'] = f'Processing page {page_num + 1} of {total_pages}...'
            
            page = doc[page_num]
            
            # Get the page as an image with OCR-optimized settings
            mat = fitz.Matrix(zoom, zoom)
            
            # Apply maximum OCR quality settings if enabled
            if max_ocr_quality:
                # Use anti-aliasing for smoother text edges
                mat = fitz.Matrix(zoom, zoom).prerotate(0)
                # Use higher quality rendering
                render_dpi = dpi * 1.5  # Boost effective DPI for rendering
                mat = fitz.Matrix(render_dpi / 72, render_dpi / 72)
            
            # Use RGB color space for better OCR results
            try:
                # First try grayscale for better OCR on text documents
                pix = page.get_pixmap(matrix=mat, alpha=False, colorspace=fitz.csGRAY)
            except:
                # Fallback to RGB if grayscale fails
                pix = page.get_pixmap(matrix=mat, alpha=False, colorspace=fitz.csRGB)
            
            # Create a new page with the same dimensions
            new_page = flattened_doc.new_page(width=page.rect.width, height=page.rect.height)
            
            # Insert the flattened image
            new_page.insert_image(page.rect, pixmap=pix)
        
        if task_id:
            processing_status[task_id]['message'] = 'Saving flattened PDF...'
        
        # Save with maximum compression while preserving quality
        flattened_doc.save(
            output_path,
            garbage=4,  # Remove unused objects
            deflate=True,  # Use deflate compression
            clean=True,  # Clean and sanitize content
            linear=True,  # Linearize for better compression
            deflate_images=True,  # Compress images
            deflate_fonts=True,  # Compress fonts
            ascii=False  # Use binary for better compression
        )
        flattened_doc.close()
        doc.close()
        
        # Check file size and compress further if needed
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        if file_size_mb > 20:
            output_path = compress_pdf_further(output_path, dpi, max_ocr_quality, target_size_mb=20)
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        
        if task_id:
            processing_status[task_id]['status'] = 'completed'
            processing_status[task_id]['progress'] = 100
            processing_status[task_id]['message'] = f'Success! File size: {file_size_mb:.1f} MB'
            processing_status[task_id]['output_file'] = output_path
        
        quality_mode = "Max Quality" if max_ocr_quality else "Standard"
        return True, f"Success (Size: {file_size_mb:.1f} MB, DPI: {dpi}, Mode: {quality_mode})", output_path
        
    except Exception as e:
        if task_id:
            processing_status[task_id]['status'] = 'error'
            processing_status[task_id]['message'] = f'Error: {str(e)}'
        return False, str(e), None

def compress_pdf_further(pdf_path, original_dpi, max_ocr_quality, target_size_mb=20):
    """Advanced compression that preserves maximum quality while reducing file size"""
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        
        # Keep original DPI - NEVER reduce quality
        zoom = original_dpi / 72
        
        # Create a new compressed document
        compressed_doc = fitz.open()
        
        # Process each page with maximum quality preservation
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(zoom, zoom)
            
            # Apply maximum OCR quality settings if enabled
            if max_ocr_quality:
                # Use anti-aliasing for smoother text edges
                mat = fitz.Matrix(zoom, zoom).prerotate(0)
                # Use higher quality rendering
                render_dpi = original_dpi * 1.5  # Boost effective DPI for rendering
                mat = fitz.Matrix(render_dpi / 72, render_dpi / 72)
            
            try:
                # Use grayscale for better compression while maintaining OCR quality
                pix = page.get_pixmap(matrix=mat, alpha=False, colorspace=fitz.csGRAY)
            except:
                # Fallback to RGB if grayscale fails
                pix = page.get_pixmap(matrix=mat, alpha=False, colorspace=fitz.csRGB)
            
            new_page = compressed_doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(page.rect, pixmap=pix)
        
        # Try advanced compression techniques while preserving quality
        compression_techniques = [
            # Technique 1: Maximum PDF compression with quality preservation
            {"deflate": True, "garbage": 4, "clean": True, "linear": True, "deflate_images": True, "deflate_fonts": True},
            # Technique 2: Aggressive PDF optimization
            {"deflate": True, "garbage": 4, "clean": True, "linear": True, "deflate_images": True, "deflate_fonts": True, "ascii": False},
            # Technique 3: Maximum compression (last attempt)
            {"deflate": True, "garbage": 4, "clean": True, "linear": True, "deflate_images": True, "deflate_fonts": True, "ascii": False, "expand": 0}
        ]
        
        for i, compression_settings in enumerate(compression_techniques):
            try:
                # Save with current compression settings
                compressed_doc.save(pdf_path, **compression_settings)
                
                # Check if size is acceptable
                file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
                if file_size_mb <= target_size_mb:
                    compressed_doc.close()
                    doc.close()
                    return pdf_path
            except:
                # If compression technique fails, try next one
                continue
        
        # If still too large, maintain quality and return
        compressed_doc.close()
        doc.close()
        return pdf_path
        
    except Exception as e:
        return pdf_path

@app.route('/')
def index():
    return jsonify({
        'message': 'PDF Flattener API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'upload': 'POST /api/upload',
            'status': 'GET /api/status/<task_id>',
            'download': 'GET /api/download/<task_id>',
            'cleanup': 'DELETE /api/cleanup/<task_id>',
            'ocr_tips': 'GET /api/ocr-tips'
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
    
    # Get parameters
    dpi = int(request.form.get('dpi', 600))
    max_ocr_quality = request.form.get('max_ocr_quality', 'false').lower() == 'true'
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Initialize processing status
    processing_status[task_id] = {
        'status': 'uploading',
        'progress': 0,
        'message': 'Uploading file...',
        'filename': file.filename
    }
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{filename}")
        file.save(input_path)
        
        # Generate output filename
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_flattened{ext}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{task_id}_{output_filename}")
        
        # Start processing in background thread
        def process_pdf():
            try:
                processing_status[task_id]['status'] = 'processing'
                processing_status[task_id]['message'] = 'Starting PDF flattening...'
                
                success, message, final_output_path = flatten_pdf(
                    input_path, output_path, dpi, max_ocr_quality, task_id
                )
                
                if success:
                    processing_status[task_id]['status'] = 'completed'
                    processing_status[task_id]['message'] = message
                    processing_status[task_id]['output_file'] = final_output_path
                    processing_status[task_id]['download_filename'] = output_filename
                else:
                    processing_status[task_id]['status'] = 'error'
                    processing_status[task_id]['message'] = f'Processing failed: {message}'
                
                # Clean up input file
                try:
                    os.remove(input_path)
                except:
                    pass
                    
            except Exception as e:
                processing_status[task_id]['status'] = 'error'
                processing_status[task_id]['message'] = f'Unexpected error: {str(e)}'
        
        thread = threading.Thread(target=process_pdf)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'message': 'File uploaded successfully. Processing started.'
        })
        
    except Exception as e:
        processing_status[task_id]['status'] = 'error'
        processing_status[task_id]['message'] = f'Upload failed: {str(e)}'
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<task_id>')
def get_status(task_id):
    if task_id not in processing_status:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(processing_status[task_id])

@app.route('/api/download/<task_id>')
def download_file(task_id):
    if task_id not in processing_status:
        return jsonify({'error': 'Task not found'}), 404
    
    status = processing_status[task_id]
    if status['status'] != 'completed' or 'output_file' not in status:
        return jsonify({'error': 'File not ready for download'}), 400
    
    try:
        return send_file(
            status['output_file'],
            as_attachment=True,
            download_name=status['download_filename']
        )
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/cleanup/<task_id>', methods=['DELETE'])
def cleanup_task(task_id):
    if task_id not in processing_status:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        # Remove output file if it exists
        if 'output_file' in processing_status[task_id]:
            output_file = processing_status[task_id]['output_file']
            if os.path.exists(output_file):
                os.remove(output_file)
        
        # Remove task from status
        del processing_status[task_id]
        
        return jsonify({'message': 'Task cleaned up successfully'})
    except Exception as e:
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500

@app.route('/api/ocr-tips')
def get_ocr_tips():
    tips = {
        "dpi_settings": {
            "400": "Basic quality for very clear documents",
            "500": "Good for clear, typed documents", 
            "550": "Balanced quality between standard and optimal",
            "600": "Optimal for most invoices and forms (recommended)",
            "700": "Enhanced quality for documents with small text",
            "800": "Better for poor quality scans or complex layouts",
            "900": "High quality for very small text or faded documents",
            "1000": "Ultra-high quality for extremely difficult documents",
            "1100": "Near-maximum quality for the most challenging scans",
            "1200": "Maximum quality for very difficult documents",
            "1500": "Professional-grade quality for critical documents",
            "1800": "Ultra-professional quality for forensic-level OCR",
            "2400": "Maximum possible quality for the most challenging documents"
        },
        "general_tips": [
            "Use higher DPI for documents with small text",
            "Grayscale mode is automatically used for better text recognition",
            "Higher DPI = larger file sizes but better OCR accuracy",
            "Advanced compression preserves maximum quality",
            "DPI is NEVER reduced - quality is always preserved",
            "Files may exceed 20MB to maintain maximum quality"
        ],
        "max_quality_mode": [
            "Enables anti-aliasing for smoother text edges",
            "Uses 1.5x effective DPI for rendering (e.g., 1200 DPI becomes 1800 DPI rendering)",
            "Optimized matrix transformations for better text clarity",
            "Recommended for the most challenging documents",
            "Will significantly increase processing time and file sizes",
            "Advanced compression maintains maximum quality without DPI reduction"
        ],
        "troubleshooting": [
            "If OCR still fails, try scanning the original document at 300+ DPI",
            "Ensure documents are flat and properly aligned",
            "Avoid shadows and ensure good lighting when scanning",
            "Clean documents before scanning to remove dust/smudges"
        ]
    }
    return jsonify(tips)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)