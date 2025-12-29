/**
 * QR Code Generator - Modern UI Script
 */

document.addEventListener('DOMContentLoaded', function() {
    localStorage.clear();
    sessionStorage.clear();
    
    initFileUpload();
    initFormSubmission();
    clearQRResult();
});

window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        clearQRResult();
        document.getElementById('qr-form').reset();
        hideFileName();
    }
});

// File Upload
function initFileUpload() {
    const fileInput = document.getElementById('logo');
    const dropZone = document.getElementById('file-drop-zone');
    const fileName = document.getElementById('file-name');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
        dropZone.addEventListener(event, e => {
            e.preventDefault();
            e.stopPropagation();
        });
    });
    
    ['dragenter', 'dragover'].forEach(event => {
        dropZone.addEventListener(event, () => dropZone.classList.add('dragover'));
    });
    
    ['dragleave', 'drop'].forEach(event => {
        dropZone.addEventListener(event, () => dropZone.classList.remove('dragover'));
    });
    
    dropZone.addEventListener('drop', e => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            showFileName(files[0].name);
        }
    });
    
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            showFileName(this.files[0].name);
        } else {
            hideFileName();
        }
    });
}

function showFileName(name) {
    const el = document.getElementById('file-name');
    el.textContent = name;
    el.style.display = 'flex';
}

function hideFileName() {
    document.getElementById('file-name').style.display = 'none';
}

// Form Submission
function initFormSubmission() {
    document.getElementById('qr-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const btn = document.getElementById('generate-btn');
        const originalText = btn.innerHTML;
        
        btn.innerHTML = '<span class="loading-spinner"></span>Generating...';
        btn.disabled = true;
        
        clearQRResult();
        removeErrors();
        
        fetch('/', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    displayQRCode(data);
                } else {
                    showError(data.error);
                }
            })
            .catch(() => showError('An error occurred. Please try again.'))
            .finally(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            });
    });
}

// QR Code Display
function displayQRCode(data) {
    const result = document.getElementById('qr-result');
    const escaped = escapeHtml(data.text);
    
    result.innerHTML = `
        <div class="message message-success">
            QR Code generated successfully
        </div>
        <div class="qr-display">
            <img src="/qr?id=${data.qr_id}&t=${Date.now()}" alt="QR Code" class="qr-code">
            <div class="qr-info">
                <div class="qr-info-label">Encoded Content</div>
                <div class="text-content">${escaped}</div>
            </div>
            <div class="download-section">
                <a href="/qr?id=${data.qr_id}&download=1" download="qrcode.png" class="btn-action btn-download">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                    </svg>
                    Download
                </a>
                <button type="button" class="btn-action" id="copy-btn">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                    </svg>
                    Copy Text
                </button>
            </div>
        </div>
    `;
    
    result.style.display = 'block';
    
    document.getElementById('copy-btn').addEventListener('click', () => copyToClipboard(data.text));
    
    result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function clearQRResult() {
    const el = document.getElementById('qr-result');
    if (el) {
        el.innerHTML = '';
        el.style.display = 'none';
    }
}

// Clipboard
async function copyToClipboard(text) {
    const btn = document.getElementById('copy-btn');
    const original = btn.innerHTML;
    
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
        } else {
            const ta = document.createElement('textarea');
            ta.value = text;
            ta.style.cssText = 'position:fixed;left:-9999px';
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
        }
        
        btn.innerHTML = `<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> Copied`;
        btn.style.background = 'var(--color-success)';
        btn.style.color = 'white';
        btn.style.border = 'none';
    } catch {
        btn.innerHTML = 'Failed';
        btn.style.background = 'var(--color-error)';
        btn.style.color = 'white';
        btn.style.border = 'none';
    }
    
    setTimeout(() => {
        btn.innerHTML = original;
        btn.style.background = '';
        btn.style.color = '';
        btn.style.border = '';
    }, 2000);
}

// Errors
function showError(msg) {
    const html = `<div class="message message-error">${escapeHtml(msg)}</div>`;
    document.querySelector('.main-content').insertAdjacentHTML('beforeend', html);
}

function removeErrors() {
    document.querySelectorAll('.message-error').forEach(el => el.remove());
}

// Utility
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}