// Global variables
let selectedFile = null;
let currentSketchData = null;

// DOM elements
const uploadBox = document.getElementById('uploadBox');
const imageInput = document.getElementById('imageInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const convertBtn = document.getElementById('convertBtn');
const btnText = document.getElementById('btnText');
const spinner = document.getElementById('spinner');
const resultSection = document.getElementById('resultSection');
const originalImage = document.getElementById('originalImage');
const sketchImage = document.getElementById('sketchImage');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

// File input change event
imageInput.addEventListener('change', function(e) {
    handleFileSelect(e.target.files[0]);
});

// Drag and drop events
uploadBox.addEventListener('dragover', function(e) {
    e.preventDefault();
    uploadBox.classList.add('dragover');
});

uploadBox.addEventListener('dragleave', function() {
    uploadBox.classList.remove('dragover');
});

uploadBox.addEventListener('drop', function(e) {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// Handle file selection
function handleFileSelect(file) {
    if (!file) return;
    
    // Check file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        showError('Please select a valid image file (JPEG, PNG, GIF, BMP, or WebP)');
        return;
    }
    
    // Check file size (16MB max)
    const maxSize = 16 * 1024 * 1024; // 16MB in bytes
    if (file.size > maxSize) {
        showError('File size must be less than 16MB');
        return;
    }
    
    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.style.display = 'flex';
    convertBtn.disabled = false;
    hideError();
    
    // Hide previous results
    resultSection.style.display = 'none';
}

// Remove selected image
function removeImage() {
    selectedFile = null;
    imageInput.value = '';
    fileInfo.style.display = 'none';
    convertBtn.disabled = true;
    resultSection.style.display = 'none';
    hideError();
}

// Convert image to sketch
async function convertToSketch() {
    if (!selectedFile) {
        showError('Please select an image first');
        return;
    }
    
    // Show loading state
    convertBtn.classList.add('loading');
    convertBtn.disabled = true;
    btnText.textContent = 'Converting...';
    hideError();
    
    // Prepare form data
    const formData = new FormData();
    formData.append('image', selectedFile);
    
    try {
        // Send request to backend
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to convert image');
        }
        
        if (data.success) {
            // Display results
            originalImage.src = data.original;
            sketchImage.src = data.sketch;
            currentSketchData = data.sketch;
            resultSection.style.display = 'block';
            
            // Smooth scroll to results
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            throw new Error(data.error || 'Conversion failed');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while converting the image');
    } finally {
        // Reset button state
        convertBtn.classList.remove('loading');
        convertBtn.disabled = false;
        btnText.textContent = 'Convert to Sketch';
    }
}

// Download sketch image
async function downloadSketch() {
    if (!currentSketchData) {
        showError('No sketch available to download');
        return;
    }
    
    try {
        const response = await fetch('/download-sketch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sketch_data: currentSketchData
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to download sketch');
        }
        
        // Create blob from response
        const blob = await response.blob();
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'pencil_sketch.png';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to download sketch');
    }
}

// Show error message
function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

// Hide error message
function hideError() {
    errorMessage.style.display = 'none';
    errorText.textContent = '';
}

// Image loading error handlers
originalImage.addEventListener('error', function() {
    this.alt = 'Failed to load original image';
});

sketchImage.addEventListener('error', function() {
    this.alt = 'Failed to load sketch image';
});

// Prevent default drag behavior for the entire document
document.addEventListener('dragover', function(e) {
    e.preventDefault();
});

document.addEventListener('drop', function(e) {
    e.preventDefault();
});