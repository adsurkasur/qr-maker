from flask import Flask, render_template, request, send_file, session, make_response, redirect
from io import BytesIO
import qrcode
from PIL import Image
import os
import tempfile
import uuid
import time
import base64

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# In-memory storage for QR codes (better for containerized environments)
qr_storage = {}

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

def cleanup_qr_storage():
    """Clean up old QR codes from memory storage"""
    current_time = time.time()
    expired_keys = []
    for key, data in qr_storage.items():
        if current_time - data['timestamp'] > 3600:  # 1 hour
            expired_keys.append(key)
    
    for key in expired_keys:
        del qr_storage[key]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # Only clear session if there's no active QR generation
        # and this isn't an AJAX request or image load
        if not session.get('qr_id') and not request.args.get('t'):
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
        
        # Save to BytesIO for in-memory storage
        img_buffer = BytesIO()
        final_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Generate unique ID for this QR code
        qr_id = str(uuid.uuid4())
        
        # Store in memory with timestamp
        qr_storage[qr_id] = {
            'data': img_buffer.getvalue(),
            'text': text,
            'timestamp': time.time()
        }
        
        # Clean up old QR codes from memory
        cleanup_qr_storage()
        
        # Store ID in session for serving
        session['qr_id'] = qr_id
        session['qr_text'] = text
        session['timestamp'] = int(time.time() * 1000)
        
        # Check if this is an AJAX request
        if is_ajax:
            # Return JSON response for AJAX
            return {
                'success': True,
                'text': text,
                'qr_id': qr_id
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
    # Try to get qr_id from URL parameter first, then fall back to session
    qr_id = request.args.get('id') or session.get('qr_id')
    
    if not qr_id:
        return 'No QR code available. Please generate one first.', 404
    
    if qr_id not in qr_storage:
        # Clean up session if QR code doesn't exist
        session.pop('qr_id', None)
        return 'QR code expired. Please generate a new one.', 404
    
    qr_data = qr_storage[qr_id]['data']
    
    # Create response from memory
    response = make_response(qr_data)
    response.headers.set('Content-Type', 'image/png')
    
    # Check if this is a download request (has download parameter) or image display
    if request.args.get('download') == '1':
        response.headers.set('Content-Disposition', 'attachment', filename='qrcode.png')
    else:
        response.headers.set('Content-Disposition', 'inline', filename='qrcode.png')
    
    # Disable caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    # Local development server
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
