from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
import base64
import io
from PIL import Image
import os
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           os.path.splitext(filename)[1].lower() in app.config['UPLOAD_EXTENSIONS']

def convert_to_pencil_sketch(image_array):
    """
    Convert an image to a realistic pencil sketch that mimics actual hand-drawn
    pencil artwork with proper shading, cross-hatching, and artistic strokes.
    """
    # Convert to grayscale
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_array.copy()
    
    # Step 1: Create the base sketch with soft edges
    # Use Difference of Gaussians for edge detection with artistic quality
    blur1 = cv2.GaussianBlur(gray, (5, 5), 1.0)
    blur2 = cv2.GaussianBlur(gray, (9, 9), 1.6)
    dog = blur1.astype(np.float32) - blur2.astype(np.float32)
    
    # Normalize and apply soft thresholding for pencil-like edges
    dog = (dog - dog.min()) / (dog.max() - dog.min() + 1e-6)
    edges = 1.0 - np.tanh(10 * (dog - 0.1))  # Soft edges
    edges = (edges * 255).astype(np.uint8)
    
    # Step 2: Create realistic shading using multiple techniques
    # Technique A: Directional strokes (simulate pencil hatching)
    kernel_sizes = [(1, 9), (9, 1), (5, 5)]  # Horizontal, vertical, and circular
    shadings = []
    
    for ksize in kernel_sizes:
        # Create directional blur to simulate pencil strokes
        kernel = cv2.getGaussianKernel(ksize[0], 1.0) @ cv2.getGaussianKernel(ksize[1], 1.0).T
        kernel = kernel / kernel.sum()
        stroke = cv2.filter2D(gray, -1, kernel)
        
        # Apply dodge blend for pencil texture
        inv_stroke = 255 - stroke
        blurred = cv2.GaussianBlur(inv_stroke, (21, 21), 0)
        shading = cv2.divide(stroke, 255 - blurred, scale=256.0)
        shadings.append(shading)
    
    # Combine different stroke directions
    combined_shading = np.mean(shadings, axis=0).astype(np.uint8)
    
    # Step 3: Create texture and grain (paper texture)
    # Add subtle noise to simulate paper grain
    noise = np.random.normal(0, 3, gray.shape)
    texture = np.clip(gray + noise, 0, 255).astype(np.uint8)
    
    # Apply bilateral filter to preserve edges while smoothing
    texture = cv2.bilateralFilter(texture, 9, 50, 50)
    
    # Step 4: Create the final sketch with proper tonal range
    # Use weighted combination of edges and shading (more weight on shading)
    sketch = cv2.addWeighted(edges, 0.4, combined_shading, 0.6, 0)
    
    # Add subtle texture
    sketch = cv2.addWeighted(sketch, 0.92, texture, 0.08, 0)
    
    # Step 5: Enhance contrast for more artistic look
    # Apply CLAHE for local contrast enhancement with higher clip limit
    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8,8))
    sketch = clahe.apply(sketch)
    
    # Step 6: Final adjustments to match real pencil sketches
    # DON'T lighten too much - keep the darker tones
    sketch = cv2.convertScaleAbs(sketch, alpha=1.1, beta=5)
    
    # Apply gamma correction for better tonal distribution
    # Lower gamma = darker image with more contrast
    gamma = 0.8  # Changed from 1.5 to 0.8 for darker result
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(256)]).astype(np.uint8)
    sketch = cv2.LUT(sketch, table)
    
    # Add slight blur for softness but not too much
    sketch = cv2.GaussianBlur(sketch, (3, 3), 0.3)
    
    # Keep the darkest areas dark (don't threshold to white)
    # Instead, only make the very brightest areas pure white
    _, white_areas = cv2.threshold(sketch, 250, 255, cv2.THRESH_BINARY)
    sketch = cv2.max(sketch, white_areas)
    
    # Additional step: Enhance mid-tones for better pencil effect
    # Create a mask for mid-tone areas
    _, dark_mask = cv2.threshold(sketch, 180, 255, cv2.THRESH_BINARY_INV)
    _, light_mask = cv2.threshold(sketch, 240, 255, cv2.THRESH_BINARY)
    mid_mask = cv2.bitwise_and(cv2.bitwise_not(dark_mask), cv2.bitwise_not(light_mask))
    
    # Slightly darken the mid-tones
    sketch = cv2.subtract(sketch, cv2.bitwise_and(mid_mask, np.full_like(mid_mask, 10)))
    
    return sketch

def image_to_base64(image_array):
    """Convert a NumPy array to base64 encoded string."""
    # Convert to PIL Image
    if len(image_array.shape) == 2:  # Grayscale
        pil_image = Image.fromarray(image_array)
    else:  # Color
        pil_image = Image.fromarray(cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB))
    
    # Save to bytes buffer
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Encode to base64
    img_str = base64.b64encode(buffer.read()).decode()
    return f"data:image/png;base64,{img_str}"

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_image():
    """Convert uploaded image to pencil sketch."""
    try:
        # Check if an image was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        
        # Check if a file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400
        
        # Read image file
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Resize image if it's too large (for performance)
        max_dimension = 1500
        height, width = image.shape[:2]
        if width > max_dimension or height > max_dimension:
            scaling_factor = max_dimension / max(width, height)
            new_width = int(width * scaling_factor)
            new_height = int(height * scaling_factor)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Convert to pencil sketch
        sketch = convert_to_pencil_sketch(image)
        
        # Convert both images to base64
        original_b64 = image_to_base64(image)
        sketch_b64 = image_to_base64(sketch)
        
        return jsonify({
            'success': True,
            'original': original_b64,
            'sketch': sketch_b64
        })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/download-sketch', methods=['POST'])
def download_sketch():
    """Generate and download the sketch image."""
    try:
        data = request.json
        sketch_data = data.get('sketch_data', '')
        
        if not sketch_data:
            return jsonify({'error': 'No sketch data provided'}), 400
        
        # Remove the data URL prefix
        if ',' in sketch_data:
            sketch_data = sketch_data.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(sketch_data)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(image_data)
            tmp_path = tmp_file.name
        
        # Send file and clean up
        def remove_file(response):
            try:
                os.remove(tmp_path)
            except:
                pass
            return response
        
        response = send_file(tmp_path, as_attachment=True, download_name='pencil_sketch.png', mimetype='image/png')
        response.call_on_close(lambda: os.remove(tmp_path))
        return response
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate download: {str(e)}'}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    # Run the app
    print("Starting Pencil Sketch App (Final Version)")
    print("Navigate to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)