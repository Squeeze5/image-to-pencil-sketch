# Image to Pencil Sketch App

A web application that converts uploaded images into beautiful pencil sketches using OpenCV and Python.

## Features

- 🎨 Convert any image to a pencil sketch
- 📤 Drag and drop or browse file upload
- 🖼️ Side-by-side comparison of original and sketch
- 💾 Download the converted sketch
- 📱 Responsive design for all devices
- ⚡ Fast processing with OpenCV

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python, Flask
- **Image Processing**: OpenCV, NumPy, Pillow
- **Styling**: Custom CSS with gradient backgrounds and animations

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. Clone or download this repository:
```bash
cd D:\image-to-pencil-sketch-app
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate
     ```
   - Windows (Command Prompt):
     ```cmd
     venv\Scripts\activate.bat
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **Upload an Image**:
   - Click the "Choose Image" button or drag and drop an image onto the upload area
   - Supported formats: JPEG, PNG, GIF, BMP, WebP
   - Maximum file size: 16MB

2. **Convert to Sketch**:
   - Click the "Convert to Sketch" button
   - Wait for the processing to complete

3. **View Results**:
   - See your original image and the pencil sketch side by side
   - Compare the transformation

4. **Download**:
   - Click "Download Sketch" to save the pencil sketch to your device

## How It Works

The application uses OpenCV's image processing capabilities to create a pencil sketch effect:

1. **Grayscale Conversion**: The image is converted to grayscale
2. **Inversion**: The grayscale image is inverted (negative)
3. **Gaussian Blur**: A blur effect is applied to the inverted image
4. **Blending**: The grayscale and blurred images are blended using color dodge blend mode
5. **Result**: A realistic pencil sketch effect is achieved

## Project Structure

```
image-to-pencil-sketch-app/
│
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
│
├── templates/
│   └── index.html        # Main HTML template
│
├── static/
│   ├── css/
│   │   └── style.css     # Application styles
│   └── js/
│       └── script.js     # Frontend JavaScript
│
└── uploads/              # Temporary upload directory (created automatically)
```

## Features in Detail

### Image Processing Algorithm

The pencil sketch conversion uses the following steps:
- Convert to grayscale for base sketch
- Apply image inversion for negative effect
- Use Gaussian blur for smoothing
- Blend using division operation for sketch effect

### Security Features

- File type validation (only image files allowed)
- File size limit (16MB maximum)
- Secure filename handling
- Input sanitization

### Performance Optimizations

- Automatic image resizing for large images (max 1500px)
- Base64 encoding for instant preview
- Efficient NumPy operations
- Client-side validation

## Troubleshooting

### Common Issues

1. **Module Not Found Error**:
   - Make sure all dependencies are installed: `pip install -r requirements.txt`

2. **Port Already in Use**:
   - Change the port in `app.py` (last line) or stop other applications using port 5000

3. **Image Not Converting**:
   - Check if the image format is supported
   - Ensure the file size is under 16MB

4. **OpenCV Installation Issues**:
   - If `opencv-python` fails to install, try:
     ```bash
     pip install --upgrade pip
     pip install opencv-python-headless
     ```

## Contributing

Feel free to fork this project and submit pull requests with improvements!

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenCV community for the powerful image processing library
- Flask framework for the simple and elegant web framework
- The gradient background design inspiration from modern web design trends
