from flask import Flask, Blueprint, jsonify, render_template, request, send_file, session, make_response, redirect
from io import BytesIO
import io
import qrcode
from PIL import Image
import os
import tempfile
import uuid
import time
import base64
import json
import zipfile
from flask_cors import CORS

# ENV VARS:
# PORT             - server port (default: 5000 dev, 7860 prod)
# QR_API_KEY       - API key for /api/* routes (optional, skipped if not set)
# FLASK_SECRET_KEY - Flask session secret key
# ALLOWED_ORIGINS  - comma-separated CORS origins (default: *)

# SVG support - try to import svg libraries (works in Docker/Linux, may fail on Windows)
SVG_SUPPORT = False
svg_converter = None
try:
    import cairosvg
    SVG_SUPPORT = True
    svg_converter = 'cairosvg'
except (ImportError, OSError):
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        SVG_SUPPORT = True
        svg_converter = 'svglib'
    except (ImportError, OSError):
        pass

def _get_allowed_origins():
    """Return allowed CORS origins from env or wildcard for development."""
    configured = os.environ.get('ALLOWED_ORIGINS', '').strip()
    if not configured:
        return '*'

    origins = [origin.strip() for origin in configured.split(',') if origin.strip()]
    return origins if origins else '*'


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": _get_allowed_origins(),
            "methods": ["POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-API-Key"],
        }
    },
)

# Supported image formats for logo (SVG only if library available)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
if SVG_SUPPORT:
    ALLOWED_EXTENSIONS.add('svg')

# In-memory storage for QR codes (better for containerized environments)
qr_storage = {}

api_bp = Blueprint('api', __name__, url_prefix='/api')


def _decode_logo_base64(logo_base64):
    """Decode and load a base64 logo string into a PIL Image in RGBA mode."""
    if not isinstance(logo_base64, str) or not logo_base64.strip():
        raise ValueError('logo_base64 must be a non-empty string when provided.')

    content = logo_base64.strip()
    mime_type = None

    if content.startswith('data:') and ',' in content:
        header, content = content.split(',', 1)
        if ';base64' not in header.lower():
            raise ValueError('logo_base64 data URL must include ;base64.')
        mime_type = header[5:].split(';', 1)[0].lower()

    try:
        logo_bytes = base64.b64decode(content, validate=True)
    except Exception:
        raise ValueError('Invalid base64 image data in logo_base64.')

    if not logo_bytes:
        raise ValueError('Decoded logo image is empty.')

    is_svg = False
    if mime_type == 'image/svg+xml':
        is_svg = True
    else:
        sniff = logo_bytes[:512].lstrip().lower()
        if sniff.startswith(b'<?xml') or sniff.startswith(b'<svg') or b'<svg' in sniff:
            is_svg = True

    if is_svg:
        if not SVG_SUPPORT:
            raise ValueError('SVG logos are not supported in this environment.')

        if svg_converter == 'cairosvg':
            import cairosvg
            png_data = cairosvg.svg2png(bytestring=logo_bytes)
            logo_img = Image.open(io.BytesIO(png_data))
        elif svg_converter == 'svglib':
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPM
            with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
                tmp.write(logo_bytes)
                tmp_path = tmp.name
            try:
                drawing = svg2rlg(tmp_path)
                if not drawing:
                    raise ValueError('Could not parse SVG logo data.')
                png_data = renderPM.drawToString(drawing, fmt='PNG')
                logo_img = Image.open(io.BytesIO(png_data))
            finally:
                os.unlink(tmp_path)
        else:
            raise ValueError('SVG logos are not supported in this environment.')
    else:
        logo_img = Image.open(io.BytesIO(logo_bytes))

    if logo_img.mode != 'RGBA':
        logo_img = logo_img.convert('RGBA')

    return logo_img


def _generate_qr_png_bytes(text, logo_img=None):
    """Generate PNG bytes for a QR code with an optional centered logo."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_pil = qr_img.convert('RGBA')

    if logo_img is not None:
        qr_width, qr_height = qr_pil.size
        logo_size = min(qr_width, qr_height) // 5

        logo_copy = logo_img.copy()
        logo_copy.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

        if logo_copy.mode == 'RGBA':
            background = Image.new('RGBA', logo_copy.size, (255, 255, 255, 255))
            logo_copy = Image.alpha_composite(background, logo_copy)

        logo_width, logo_height = logo_copy.size
        x = (qr_width - logo_width) // 2
        y = (qr_height - logo_height) // 2
        qr_pil.paste(logo_copy, (x, y), logo_copy if logo_copy.mode == 'RGBA' else None)

    final_img = qr_pil.convert('RGB')
    img_buffer = BytesIO()
    final_img.save(img_buffer, format='PNG')
    return img_buffer.getvalue()


def _get_bulk_item_id(item, index):
    """Return item id or a stringified index fallback."""
    if not isinstance(item, dict):
        return str(index)

    raw_id = item.get('id')
    if raw_id is None:
        return str(index)

    item_id = str(raw_id).strip()
    return item_id if item_id else str(index)


@api_bp.before_request
def _api_key_guard():
    """Protect API routes when QR_API_KEY is configured."""
    if request.method == 'OPTIONS':
        return None

    expected_api_key = os.environ.get('QR_API_KEY')
    if not expected_api_key:
        return None

    provided_api_key = request.headers.get('X-API-Key', '')
    if provided_api_key != expected_api_key:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    return None


@api_bp.route('/qr/single', methods=['POST', 'OPTIONS'])
def api_qr_single():
    if request.method == 'OPTIONS':
        return ('', 204)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({'success': False, 'error': 'Request body must be valid JSON.'}), 400

    text = str(payload.get('text', '')).strip()
    logo_base64 = payload.get('logo_base64')

    if not text:
        return jsonify({'success': False, 'error': 'Please provide text.'}), 400

    if len(text) > 1000:
        return jsonify({'success': False, 'error': 'Text is too long. Maximum 1000 characters allowed.'}), 400

    try:
        logo_img = None
        if logo_base64 is not None:
            logo_img = _decode_logo_base64(logo_base64)

        qr_png = _generate_qr_png_bytes(text, logo_img)
        image_base64 = base64.b64encode(qr_png).decode('ascii')
        return jsonify({'success': True, 'image_base64': image_base64, 'format': 'png'}), 200
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400
    except Exception as exc:
        return jsonify({'success': False, 'error': f'Error generating QR code: {str(exc)}'}), 500


@api_bp.route('/qr/bulk', methods=['POST', 'OPTIONS'])
def api_qr_bulk():
    if request.method == 'OPTIONS':
        return ('', 204)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({'success': False, 'error': 'Request body must be valid JSON.'}), 400

    items = payload.get('items')
    if not isinstance(items, list) or not items:
        return jsonify({'success': False, 'error': 'items is required and must be a non-empty array.'}), 400

    if len(items) > 200:
        return jsonify({'success': False, 'error': 'items exceeds maximum of 200.'}), 400

    global_logo_base64 = payload.get('logo_base64')
    global_logo_img = None
    global_logo_error = None
    if global_logo_base64 is not None:
        try:
            global_logo_img = _decode_logo_base64(global_logo_base64)
        except ValueError as exc:
            global_logo_error = str(exc)

    errors = []
    success_count = 0
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
        for index, item in enumerate(items):
            item_id = _get_bulk_item_id(item, index)

            if not isinstance(item, dict):
                errors.append({'id': item_id, 'error': 'Item must be an object.'})
                continue

            text = str(item.get('text', '')).strip()
            if not text:
                errors.append({'id': item_id, 'error': 'Please provide text.'})
                continue

            if len(text) > 1000:
                errors.append({'id': item_id, 'error': 'Text is too long. Maximum 1000 characters allowed.'})
                continue

            try:
                logo_img = None
                if item.get('logo_base64') is not None:
                    logo_img = _decode_logo_base64(item.get('logo_base64'))
                elif global_logo_base64 is not None:
                    if global_logo_error:
                        raise ValueError(global_logo_error)
                    logo_img = global_logo_img

                qr_png = _generate_qr_png_bytes(text, logo_img)
                zip_file.writestr(f'{item_id}.png', qr_png)
                success_count += 1
            except Exception as exc:
                errors.append({'id': item_id, 'error': str(exc)})

        summary = {
            'total': len(items),
            'success': success_count,
            'failed': len(items) - success_count,
            'errors': errors,
        }
        zip_file.writestr('summary.json', json.dumps(summary, indent=2))

    if success_count == 0:
        return jsonify({'success': False, 'error': 'All items failed.', 'errors': errors}), 422

    zip_buffer.seek(0)
    response = make_response(zip_buffer.getvalue())
    response.headers.set('Content-Type', 'application/zip')
    response.headers.set('Content-Disposition', f'attachment; filename=qr_bulk_{int(time.time())}.zip')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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
            file_ext = logo_file.filename.lower().rsplit('.', 1)[-1] if '.' in logo_file.filename else ''
            if file_ext not in ALLOWED_EXTENSIONS:
                allowed_list = ', '.join(sorted(ALLOWED_EXTENSIONS)).upper()
                if is_ajax:
                    return {'success': False, 'error': f'Unsupported file format. Allowed: {allowed_list}'}
                session['error'] = f'Unsupported file format. Allowed: {allowed_list}'
                return render_template('index.html', error=session['error'])
            
            try:
                # Handle SVG files - convert to PNG first
                if file_ext == 'svg':
                    svg_data = logo_file.read()
                    if svg_converter == 'cairosvg':
                        import cairosvg
                        png_data = cairosvg.svg2png(bytestring=svg_data)
                        logo_img = Image.open(io.BytesIO(png_data))
                    elif svg_converter == 'svglib':
                        from svglib.svglib import svg2rlg
                        from reportlab.graphics import renderPM
                        # Write SVG to temp file for svglib
                        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
                            tmp.write(svg_data)
                            tmp_path = tmp.name
                        try:
                            drawing = svg2rlg(tmp_path)
                            if drawing:
                                png_data = renderPM.drawToString(drawing, fmt='PNG')
                                logo_img = Image.open(io.BytesIO(png_data))
                            else:
                                raise ValueError("Could not parse SVG file")
                        finally:
                            os.unlink(tmp_path)
                    else:
                        raise ValueError("SVG support not available")
                else:
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


app.register_blueprint(api_bp)

if __name__ == '__main__':
    # Local development server
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
