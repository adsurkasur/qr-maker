from flask import Flask, render_template, request, send_file, session, make_response, redirect
from io import BytesIO
import qrcode
from PIL import Image
import os
import tempfile
import uuid
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

def cleanup_old_qr_files():
    """Clean up old QR code temporary files"""
    temp_dir = tempfile.gettempdir()
    for filename in os.listdir(temp_dir):
        if filename.startswith('qr_') and filename.endswith('.png'):
            filepath = os.path.join(temp_dir, filename)
            try:
                # Remove files older than 1 hour
                if os.path.getctime(filepath) < time.time() - 3600:
                    os.remove(filepath)
            except (OSError, FileNotFoundError):
                pass

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # Clear any session data on GET requests
        session.clear()
        
        response = make_response(render_template('index.html', 
                         error=None))
        # Prevent page caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    # POST request - generate QR code
    # Clean up old temporary files
    cleanup_old_qr_files()
    
    text = request.form.get('text', '').strip()
    
    # Check if this is an AJAX request
    is_ajax = request.form.get('ajax') == '1'
    
    if not text:
        if is_ajax:
            return {'success': False, 'error': 'Please enter some text to encode.'}
        session['error'] = 'Please enter some text to encode.'
        return render_template('index.html', error=session['error'])
    
    if len(text) > 1000:
        if is_ajax:
            return {'success': False, 'error': 'Text is too long. Maximum 1000 characters allowed.'}
        session['error'] = 'Text is too long. Maximum 1000 characters allowed.'
        return render_template('index.html', error=session['error'])
    
    try:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Higher error correction for logo
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to PIL Image for logo overlay
        qr_pil = qr_img.convert('RGBA')
        
        # Handle logo upload
        logo_file = request.files.get('logo')
        if logo_file and logo_file.filename:
            # Validate file type
            if not logo_file.filename.lower().endswith('.png'):
                if is_ajax:
                    return {'success': False, 'error': 'Only PNG files are allowed for logos.'}
                session['error'] = 'Only PNG files are allowed for logos.'
                return render_template('index.html', error=session['error'])
            
            try:
                # Open and process logo
                logo_img = Image.open(logo_file)
                
                # Convert to RGBA if not already
                if logo_img.mode != 'RGBA':
                    logo_img = logo_img.convert('RGBA')
                
                # Calculate logo size (20% of QR code size)
                qr_width, qr_height = qr_pil.size
                logo_size = min(qr_width, qr_height) // 5  # 20% of smaller dimension
                
                # Resize logo while maintaining aspect ratio
                logo_img.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # Create white background for logo if it has transparency
                if logo_img.mode == 'RGBA':
                    # Create white background
                    background = Image.new('RGBA', logo_img.size, (255, 255, 255, 255))
                    # Composite logo onto white background
                    logo_with_bg = Image.alpha_composite(background, logo_img)
                    logo_img = logo_with_bg
                
                # Calculate position to center the logo
                logo_width, logo_height = logo_img.size
                x = (qr_width - logo_width) // 2
                y = (qr_height - logo_height) // 2
                
                # Paste logo onto QR code
                qr_pil.paste(logo_img, (x, y), logo_img if logo_img.mode == 'RGBA' else None)
                
            except Exception as logo_error:
                if is_ajax:
                    return {'success': False, 'error': f'Error processing logo: {str(logo_error)}'}
                session['error'] = f'Error processing logo: {str(logo_error)}'
                return render_template('index.html', error=session['error'])
        
        # Convert back to RGB for PNG output
        final_img = qr_pil.convert('RGB')
        
        # Save to temporary file
        temp_filename = f"qr_{uuid.uuid4().hex}.png"
        temp_filepath = os.path.join(tempfile.gettempdir(), temp_filename)
        final_img.save(temp_filepath, format='PNG')
        
        # Store in session for serving
        session['qr_filename'] = temp_filename
        session['qr_text'] = text
        session['timestamp'] = int(time.time() * 1000)
        
        # Check if this is an AJAX request
        if is_ajax:
            # Return JSON response for AJAX
            return {
                'success': True,
                'text': text,
                'filename': temp_filename
            }
        else:
            # Fallback for non-AJAX requests (redirect)
            session['fresh_generation'] = True
            session['qr_generated'] = True
            session.pop('error', None)
            return redirect('/', code=303)
        
    except Exception as e:
        if is_ajax:
            return {'success': False, 'error': f'Error generating QR code: {str(e)}'}
        session['error'] = f'Error generating QR code: {str(e)}'
        return render_template('index.html', error=session['error'])

@app.route('/qr')
def get_qr():
    if 'qr_filename' not in session:
        return 'No QR code available. Please generate one first.', 404
    
    temp_filepath = os.path.join(tempfile.gettempdir(), session['qr_filename'])
    
    if not os.path.exists(temp_filepath):
        # Clean up session if file doesn't exist
        session.pop('qr_filename', None)
        session.pop('qr_generated', None)
        return 'QR code expired. Please generate a new one.', 404
    
    response = send_file(temp_filepath, mimetype='image/png', as_attachment=False, download_name='qrcode.png')
    # Disable caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # For production deployment (like Hugging Face Spaces)
    # Hugging Face Spaces expects the app to run on port 7860
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
