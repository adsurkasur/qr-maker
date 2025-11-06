# QR Code Generator

A simple web application that generates QR codes in PNG format using Python Flask.

## Features

- Generate QR codes from any text input
- PNG format output
- Simple web interface
- Downloadable QR codes
- Input validation and error handling

## Installation

1. Clone or download this repository
2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

4. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start (Windows)
Simply double-click `run.bat` to start the application!

---
title: QR Code Generator
emoji: 📱
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---

# QR Code Generator

A simple web application that generates QR codes in PNG format using Python Flask.

## Features

- Generate QR codes from any text input
- PNG format output with optional logo overlay
- Simple web interface
- Downloadable QR codes
- Input validation and error handling
- AJAX-powered for smooth user experience

## Installation

1. Clone or download this repository
2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

4. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start (Windows)
Simply double-click `run.bat` to start the application!

### Manual Setup

1. Activate the virtual environment (if not already activated):

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

2. Run the application:

```bash
python app.py
```

3. Open your web browser and navigate to `http://localhost:5000`

## Deployment on Hugging Face Spaces

This application can be deployed on Hugging Face Spaces for free hosting:

1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Choose "Docker" as the SDK
3. Upload all files from this repository
4. The Space will automatically build and deploy your QR code generator

See `DEPLOYMENT.md` for detailed instructions.

## Local Development

- `GET /` - Main page with QR code generator form
- `POST /` - Generate QR code (accepts form data with 'text' and optional 'logo' file)
- `GET /qr` - Serve generated QR code image

## Technologies Used

- **Flask** - Web framework
- **qrcode[pil]** - QR code generation library
- **Pillow** - Image processing for logo overlay
- **HTML/CSS/JavaScript** - Frontend interface

## License

This project is open source and available under the MIT License.

2. Run the Flask application:

```bash
python app.py
```

3. Open your web browser and go to http://localhost:5000

4. Enter any text, URL, or message in the input field

5. Click "Generate QR Code" to create your QR code

6. The QR code will be displayed and you can download it as a PNG file

## Requirements

- Python 3.9+
- Flask 3.0.0
- qrcode 8.2 with PIL support

## How it works

- The application uses the qrcode library to generate QR codes
- Images are created in memory using BytesIO buffers (no files saved to disk)
- Flask serves the generated images dynamically
- The web interface is built with simple HTML and CSS

## Security Note

This is a basic demo application. In production, you would want to:
- Use a proper secret key for sessions
- Implement rate limiting
- Add proper error logging
- Use a more robust storage solution for images if needed
- Add authentication if required

## License

This project is open source and available under the MIT License.
