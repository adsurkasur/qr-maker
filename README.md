---
title: QR Code Generator
emoji: 🎨
colorFrom: blue
colorTo: purple
sdk: docker
app_file: app.py
pinned: false
---

# 🎨 QR Code Generator

A beautiful web application that generates custom QR codes with logo overlay using Python Flask.

## ✨ Features

- 🎯 Generate QR codes from any text input (URLs, messages, etc.)
- 🖼️ Add custom PNG logos to QR codes
- 📱 Modern, responsive web interface
- 📥 Download QR codes as PNG files
- 📋 Copy encoded text to clipboard
- 🎭 Drag & drop logo upload
- ⚡ AJAX-powered for instant results
- 📱 Mobile-friendly design

## 🚀 Live Demo

This app can be deployed instantly on [Hugging Face Spaces](https://huggingface.co/spaces) for free!

## 🌐 Custom Domain Setup

### Option 1: Hugging Face Spaces Custom Domain (Recommended)

1. **Go to your Space Settings**:
   - Visit your Hugging Face Space
   - Click the "Settings" tab
   - Scroll down to "Custom Domain"

2. **Add your domain**:
   - Enter your domain name (e.g., `qr.yourdomain.com`)
   - Click "Add Domain"

3. **Configure DNS**:
   - Hugging Face will provide CNAME records
   - Add these records to your domain's DNS settings

### Option 2: Direct CNAME (Alternative)

If Hugging Face's built-in custom domain isn't available:

1. **Get your Space URL**:
   - Your Space URL: `https://[username]-[space-name].hf.space`

2. **Configure DNS**:
   - Add a CNAME record pointing to: `[username]-[space-name].hf.space`
   - For example: `qr.yourdomain.com CNAME [username]-[space-name].hf.space`

3. **SSL Certificate**:
   - Hugging Face automatically provides SSL certificates
   - Your custom domain will be HTTPS-enabled

### Option 3: Cloudflare Pages (Advanced)

For more control over routing and caching:

1. **Create a Cloudflare Pages project**
2. **Set up as a reverse proxy**:
   ```javascript
   // _redirects file
   /* https://[username]-[space-name].hf.space/:splat 200
   ```

3. **Configure custom domain in Cloudflare**

## 📋 Domain Requirements

- **Domain Ownership**: You must own the domain
- **DNS Access**: Ability to modify DNS records
- **Propagation Time**: DNS changes take 24-48 hours to propagate

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

## 🚀 Deploy to Hugging Face Spaces

### Quick Deploy (2 minutes)

1. **Go to [Hugging Face Spaces](https://huggingface.co/spaces)**
2. **Click "Create new Space"**
3. **Fill in details:**
   - **Space name**: `qr-code-generator` (or your choice)
   - **License**: MIT
   - **SDK**: Docker
   - **Visibility**: Public
4. **Upload files** from this repository
5. **Deploy** - Hugging Face handles everything automatically!

### Your Live App URL
```
https://[your-username]-qr-code-generator.hf.space
```

### Files to Upload
- ✅ `app.py` - Flask application
- ✅ `requirements.txt` - Dependencies
- ✅ `Dockerfile` - Container config
- ✅ `README.md` - Space metadata
- ✅ `templates/index.html` - UI
- ✅ `.gitattributes` - File handling

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
