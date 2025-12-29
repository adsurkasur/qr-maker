# Hugging Face Spaces Deployment Guide

## Quick Deploy Steps

1. **Create a Hugging Face Account**
   - Go to [huggingface.co](https://huggingface.co) and sign up

2. **Create a New Space**
   - Click "New Space" on your profile
   - Name: `qr-code-generator` (or your choice)
   - License: MIT
   - SDK: Docker
   - Visibility: Public

3. **Upload Files**
   - Upload all files from this project:
     - `app.py`
     - `requirements.txt`
     - `Dockerfile`
     - `README.md`
     - `templates/` folder
     - `.gitattributes`

4. **Deploy**
   - Hugging Face will automatically build and deploy
   - Your app will be live at: `https://[your-username]-qr-code-generator.hf.space`

## Files Needed for Deployment

- ✅ `app.py` - Flask application
- ✅ `requirements.txt` - Python dependencies
- ✅ `Dockerfile` - Container configuration
- ✅ `README.md` - Space metadata
- ✅ `templates/index.html` - HTML template
- ✅ `.gitattributes` - File handling config

## Troubleshooting

- **Port Issues**: App runs on port 7860 (Hugging Face standard)
- **File Uploads**: Logo uploads work in containers
- **Sessions**: Flask sessions work in Spaces
- **Temp Files**: Uses container temp directory

## Alternative Deployment Options

- **Vercel**: Use `vercel.json` config
- **Railway**: Direct GitHub integration
- **Render**: Web service deployment
- **Heroku**: Traditional PaaS deployment