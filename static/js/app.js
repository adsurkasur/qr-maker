/**
 * QR Code Generator - Modern UI Script
 */

document.addEventListener('DOMContentLoaded', function() {
    localStorage.clear();
    sessionStorage.clear();
    
    initFileUpload();
    initFormSubmission();
    initDonationModal();
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
    const mainContent = document.querySelector('.main-content');
    const result = document.getElementById('qr-result');
    const escaped = escapeHtml(data.text);
    
    // Set content
    result.innerHTML = `
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
    
    document.getElementById('copy-btn').addEventListener('click', () => copyToClipboard(data.text));
    
    // Show result section
    mainContent.classList.add('has-qr');
    result.classList.add('visible');
    
    // Scroll to QR code on mobile - wait for image to load
    if (window.innerWidth <= 768) {
        const qrImage = result.querySelector('.qr-code');
        if (qrImage) {
            const performScroll = () => {
                // Scroll to the bottom of the result section in one smooth motion
                result.scrollIntoView({ behavior: 'smooth', block: 'end' });
            };
            
            qrImage.onload = performScroll;
            // Fallback if image is cached
            if (qrImage.complete) {
                performScroll();
            }
        }
    }
}

function clearQRResult() {
    const mainContent = document.querySelector('.main-content');
    const el = document.getElementById('qr-result');
    if (mainContent) {
        mainContent.classList.remove('has-qr');
    }
    if (el) {
        el.classList.remove('visible');
        el.innerHTML = '';
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
            ta.style.cssText = 'position:fixed;left:-9999px;top:0';
            document.body.appendChild(ta);
            ta.focus();
            ta.select();
            const success = document.execCommand('copy');
            document.body.removeChild(ta);
            if (!success) throw new Error('Copy command failed');
        }
        
        btn.innerHTML = `<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> Copied`;
        btn.style.background = 'var(--color-success)';
        btn.style.color = 'white';
        btn.style.border = 'none';
    } catch (err) {
        console.error('Copy failed:', err);
        btn.innerHTML = `<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg> Failed`;
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

// Donation Modal
function initDonationModal() {
    const modal = document.getElementById('donation-modal');
    const openBtn = document.getElementById('donate-btn');
    const closeBtn = document.getElementById('modal-close');
    
    // QRIS Modal
    const qrisModal = document.getElementById('qris-modal');
    const qrisCard = document.getElementById('qris-card');
    const qrisCloseBtn = document.getElementById('qris-modal-close');
    
    if (!modal || !openBtn) return;
    
    // Open donation modal
    openBtn.addEventListener('click', () => {
        modal.classList.add('visible');
        document.body.style.overflow = 'hidden';
    });
    
    // Close donation modal
    function closeModal() {
        modal.classList.remove('visible');
        document.body.style.overflow = '';
    }
    
    closeBtn.addEventListener('click', closeModal);
    
    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // QRIS Modal handlers
    if (qrisCard && qrisModal) {
        qrisCard.addEventListener('click', () => {
            qrisModal.classList.add('visible');
        });
        
        function closeQrisModal() {
            qrisModal.classList.remove('visible');
        }
        
        qrisCloseBtn.addEventListener('click', closeQrisModal);
        
        qrisModal.addEventListener('click', (e) => {
            if (e.target === qrisModal) {
                closeQrisModal();
            }
        });
        
        // QRIS Download handler
        const qrisDownloadBtn = document.getElementById('qris-download-btn');
        if (qrisDownloadBtn) {
            qrisDownloadBtn.addEventListener('click', async () => {
                const imageUrl = 'https://purple-given-lark-169.mypinata.cloud/ipfs/bafkreihplwmmtmq6youvqcfpiks4mffrdzc54h5ymqhfiq63bzzjfdiugq';
                const originalText = qrisDownloadBtn.innerHTML;
                
                try {
                    qrisDownloadBtn.innerHTML = '<span class="loading-spinner"></span>Downloading...';
                    qrisDownloadBtn.disabled = true;
                    
                    const response = await fetch(imageUrl);
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'qris-ade.jpg';
                    document.body.appendChild(a);
                    a.click();
                    
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    qrisDownloadBtn.innerHTML = originalText;
                    qrisDownloadBtn.disabled = false;
                } catch (error) {
                    console.error('Download failed:', error);
                    qrisDownloadBtn.innerHTML = originalText;
                    qrisDownloadBtn.disabled = false;
                }
            });
        }
    }
    
    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (qrisModal && qrisModal.classList.contains('visible')) {
                qrisModal.classList.remove('visible');
            } else if (modal.classList.contains('visible')) {
                closeModal();
            }
        }
    });
    
    // Copy crypto addresses
    const cryptoCards = document.querySelectorAll('.donation-card[data-crypto]');
    cryptoCards.forEach(card => {
        card.addEventListener('click', () => {
            const address = card.dataset.address;
            if (address) {
                copyCryptoAddress(card, address);
            }
        });
    });
}

// Copy crypto address with visual feedback
async function copyCryptoAddress(card, address) {
    const copyIcon = card.querySelector('.copy-icon');
    const checkIcon = card.querySelector('.check-icon');
    const badge = card.querySelector('.copy-badge');
    
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(address);
        } else {
            const ta = document.createElement('textarea');
            ta.value = address;
            ta.style.cssText = 'position:fixed;left:-9999px;top:0';
            document.body.appendChild(ta);
            ta.focus();
            ta.select();
            const success = document.execCommand('copy');
            document.body.removeChild(ta);
            if (!success) throw new Error('Copy command failed');
        }
        
        // Show success feedback
        if (copyIcon) copyIcon.style.display = 'none';
        if (checkIcon) {
            checkIcon.style.display = 'block';
            checkIcon.style.color = 'var(--color-success)';
        }
        if (badge) badge.style.display = 'inline-flex';
        
        // Reset after delay
        setTimeout(() => {
            if (copyIcon) copyIcon.style.display = 'block';
            if (checkIcon) checkIcon.style.display = 'none';
            if (badge) badge.style.display = 'none';
        }, 3000);
        
    } catch (err) {
        console.error('Failed to copy address:', err);
    }
}