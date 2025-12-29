/**
 * QR Code Generator - Main Application Script
 * Handles form submission, file uploads, and QR code display
 */

// ========================================
// INITIALIZATION
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Clear browser storage on load
    localStorage.clear();
    sessionStorage.clear();
    
    // Initialize components
    initFileUpload();
    initFormSubmission();
    initInputEffects();
    
    // Clear any QR results on page load/refresh
    clearQRResult();
});

// Handle browser back/forward navigation
window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        clearQRResult();
        document.getElementById('qr-form').reset();
        document.getElementById('file-name').style.display = 'none';
    }
});

// ========================================
// FILE UPLOAD HANDLING
// ========================================

function initFileUpload() {
    const fileInput = document.getElementById('logo');
    const fileDropZone = document.getElementById('file-drop-zone');
    const fileNameDisplay = document.getElementById('file-name');
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileDropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Highlight drop zone on drag
    ['dragenter', 'dragover'].forEach(eventName => {
        fileDropZone.addEventListener(eventName, () => {
            fileDropZone.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        fileDropZone.addEventListener(eventName, () => {
            fileDropZone.classList.remove('dragover');
        }, false);
    });
    
    // Handle file drop
    fileDropZone.addEventListener('drop', function(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            updateFileName(files[0]);
        }
    }, false);
    
    // Handle file input change
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            updateFileName(this.files[0]);
        } else {
            fileNameDisplay.style.display = 'none';
        }
    });
    
    function updateFileName(file) {
        fileNameDisplay.textContent = '📎 ' + file.name;
        fileNameDisplay.style.display = 'block';
    }
}

// ========================================
// FORM SUBMISSION
// ========================================

function initFormSubmission() {
    const form = document.getElementById('qr-form');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const submitButton = document.getElementById('generate-btn');
        const originalText = submitButton.innerHTML;
        
        // Show loading state
        submitButton.innerHTML = '<span class="loading-spinner"></span>Generating...';
        submitButton.disabled = true;
        
        // Clear previous results
        clearQRResult();
        removeExistingErrors();
        
        // Send AJAX request
        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayQRCode(data);
            } else {
                showError(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred while generating the QR code.');
        })
        .finally(() => {
            // Reset button state
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        });
    });
}

// ========================================
// QR CODE DISPLAY
// ========================================

function displayQRCode(data) {
    const resultSection = document.getElementById('qr-result');
    
    // Escape special characters for use in onclick attribute
    const escapedText = escapeHtml(data.text);
    
    const qrHtml = `
        <div class="message message-success">
            ✨ QR Code generated successfully!
        </div>
        <div class="qr-display">
            <img src="/qr?id=${data.qr_id}&t=${Date.now()}" alt="Generated QR Code" class="qr-code">
            <div class="qr-info">
                <strong>📝 Encoded Text:</strong>
                <div class="text-content">${escapedText}</div>
            </div>
            <div class="download-section">
                <a href="/qr?id=${data.qr_id}&download=1" download="qrcode.png" class="btn-action">
                    📥 Download PNG
                </a>
                <button type="button" class="btn-action" id="copy-btn">
                    📋 Copy Text
                </button>
            </div>
        </div>
    `;
    
    resultSection.innerHTML = qrHtml;
    resultSection.style.display = 'block';
    
    // Add click handler for copy button
    document.getElementById('copy-btn').addEventListener('click', function() {
        copyToClipboard(data.text);
    });
    
    // Scroll to result
    resultSection.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest'
    });
}

function clearQRResult() {
    const resultSection = document.getElementById('qr-result');
    if (resultSection) {
        resultSection.innerHTML = '';
        resultSection.style.display = 'none';
    }
}

// ========================================
// CLIPBOARD FUNCTIONALITY
// ========================================

async function copyToClipboard(text) {
    const copyBtn = document.getElementById('copy-btn');
    const originalText = copyBtn.innerHTML;
    
    try {
        // Try modern clipboard API first
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers or non-HTTPS
            fallbackCopyToClipboard(text);
        }
        
        // Show success feedback
        copyBtn.innerHTML = '✅ Copied!';
        copyBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
        
    } catch (err) {
        console.error('Failed to copy text:', err);
        
        // Show error feedback
        copyBtn.innerHTML = '❌ Failed to copy';
        copyBtn.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
    }
    
    // Reset after 2 seconds
    setTimeout(() => {
        copyBtn.innerHTML = originalText;
        copyBtn.style.background = '';
    }, 2000);
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
    } finally {
        document.body.removeChild(textArea);
    }
}

// ========================================
// ERROR HANDLING
// ========================================

function showError(message) {
    const errorHtml = '<div class="message message-error">' + escapeHtml(message) + '</div>';
    document.querySelector('.main-content').insertAdjacentHTML('beforeend', errorHtml);
}

function removeExistingErrors() {
    const existingError = document.querySelector('.message-error');
    if (existingError) {
        existingError.remove();
    }
}

// ========================================
// INPUT EFFECTS
// ========================================

function initInputEffects() {
    document.querySelectorAll('input[type="text"]').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'translateY(-2px)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'translateY(0)';
        });
    });
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}