from flask import Flask, render_template, request, send_file, session
from io import BytesIO
import qrcode

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

@app.route('/')
def index():
    return render_template('index.html', 
                         error=session.pop('error', None),
                         qr_generated=session.get('qr_generated', False))

@app.route('/generate', methods=['POST'])
def generate_qr():
    text = request.form.get('text', '').strip()
    
    if not text:
        session['error'] = 'Please enter some text to encode.'
        session['qr_generated'] = False
        return render_template('index.html', error=session['error'], qr_generated=False)
    
    if len(text) > 1000:
        session['error'] = 'Text is too long. Maximum 1000 characters allowed.'
        session['qr_generated'] = False
        return render_template('index.html', error=session['error'], qr_generated=False)
    
    try:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO buffer
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Store the image data in session (for this simple demo)
        # In production, you'd want to use a more robust storage solution
        session['qr_image'] = img_buffer.getvalue()
        session['qr_generated'] = True
        session.pop('error', None)
        
        return render_template('index.html', qr_generated=True)
        
    except Exception as e:
        session['error'] = f'Error generating QR code: {str(e)}'
        session['qr_generated'] = False
        return render_template('index.html', error=session['error'], qr_generated=False)

@app.route('/qr')
def get_qr():
    if 'qr_image' not in session:
        return 'No QR code available', 404
    
    # Create a new BytesIO from the stored image data
    img_buffer = BytesIO(session['qr_image'])
    img_buffer.seek(0)
    
    return send_file(img_buffer, mimetype='image/png', as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
