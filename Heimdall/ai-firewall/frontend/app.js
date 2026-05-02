const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const fileNameDisplay = document.getElementById('file-name');
const removeBtn = document.getElementById('remove-file');
const scanBtn = document.getElementById('scan-btn');
const resultContainer = document.getElementById('result-container');

const resultStatus = document.getElementById('result-status');
const resultScanId = document.getElementById('result-scan-id');
const resultFilename = document.getElementById('result-filename');
const resultMessage = document.getElementById('result-message');

let currentFile = null;

// Drag & Drop Handlers
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-active');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-active');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-active');
    
    if (e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

removeBtn.addEventListener('click', () => {
    currentFile = null;
    fileInput.value = '';
    fileInfo.classList.add('hidden');
    dropZone.style.display = 'block';
    scanBtn.disabled = true;
    resultContainer.classList.add('hidden');
});

function handleFileSelect(file) {
    currentFile = file;
    fileNameDisplay.textContent = file.name;
    dropZone.style.display = 'none';
    fileInfo.classList.remove('hidden');
    scanBtn.disabled = false;
    resultContainer.classList.add('hidden');
}

// Upload Logic
scanBtn.addEventListener('click', async () => {
    if (!currentFile) return;

    // Loading state
    scanBtn.disabled = true;
    scanBtn.innerHTML = '<span class="loading">Scanning Document...</span>';
    resultContainer.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', currentFile);

    try {
        const response = await fetch('http://127.0.0.1:8000/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (!response.ok && data.error) {
            // Handle custom 403 blocks from policy engine
            displayResult('blocked', 'N/A', currentFile.name, data.error.message || data.error);
        } else {
            // Handle success responses
            displayResult(data.status, data.scan_id, data.filename, data.message);
        }

    } catch (error) {
        console.error("Upload error:", error);
        displayResult('error', 'N/A', currentFile.name, 'Failed to connect to the Heimdall Firewall server. Please ensure the backend is running.');
    } finally {
        scanBtn.disabled = false;
        scanBtn.textContent = 'Scan Document';
    }
});

function displayResult(status, scanId, filename, message) {
    resultContainer.classList.remove('hidden');
    
    // Reset classes
    resultStatus.className = 'badge';
    
    // Style the status badge
    let statusClass = 'status-processing'; // default green
    if (status === 'blocked' || status === 'error') statusClass = 'status-blocked';
    if (status === 'awaiting_consent') statusClass = 'status-awaiting_consent';
    if (status === 'complete') statusClass = 'status-complete';
    
    resultStatus.classList.add(statusClass);
    resultStatus.textContent = status || 'Unknown';
    
    resultScanId.textContent = scanId || 'N/A';
    resultFilename.textContent = filename || 'Unknown';
    
    // Specific message styling
    const messageContainer = document.querySelector('.message-box p');
    if (status === 'blocked' || status === 'error') {
        messageContainer.style.borderLeftColor = 'var(--error)';
    } else if (status === 'awaiting_consent') {
        messageContainer.style.borderLeftColor = 'var(--warning)';
    } else {
        messageContainer.style.borderLeftColor = 'var(--success)';
    }

    resultMessage.textContent = message || 'Scan complete.';
    
    // Handle redacted output container
    const outputContainer = document.getElementById('redacted-output-container');
    const outputText = document.getElementById('result-redacted-text');
    outputContainer.classList.add('hidden');
    outputText.textContent = '';
    
    // Handle consent panel
    const consentPanel = document.getElementById('consent-panel');
    consentPanel.classList.add('hidden');

    if (status === 'awaiting_consent' && scanId && scanId !== 'N/A') {
        // Show the consent panel with Approve/Deny buttons
        consentPanel.classList.remove('hidden');
        
        // Store the scan ID on the panel so the button handlers can read it
        consentPanel.dataset.scanId = scanId;
    }
    
    if (status === 'complete' && scanId && scanId !== 'N/A') {
        // Automatically fetch the redacted text!
        fetch(`http://127.0.0.1:8000/document/${scanId}/redacted`)
            .then(res => res.json())
            .then(data => {
                if (data.redacted_text) {
                    outputText.textContent = data.redacted_text;
                    outputContainer.classList.remove('hidden');
                }
            })
            .catch(err => console.error("Could not fetch redacted text:", err));
    }
    
    // Smooth scroll to results
    setTimeout(() => {
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// --- Consent Flow Handlers ---

async function handleConsent(approved) {
    const consentPanel = document.getElementById('consent-panel');
    const scanId = consentPanel.dataset.scanId;
    
    if (!scanId) return;
    
    // Disable both buttons immediately to prevent double-clicks
    const approveBtn = document.getElementById('consent-approve');
    const denyBtn = document.getElementById('consent-deny');
    approveBtn.disabled = true;
    denyBtn.disabled = true;
    
    const actionText = approved ? 'Approving...' : 'Denying...';
    if (approved) approveBtn.textContent = actionText;
    else denyBtn.textContent = actionText;
    
    try {
        const response = await fetch(`http://127.0.0.1:8000/scan/${scanId}/consent`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                scan_id: scanId,
                approved: approved,
                user_note: approved ? "Approved via frontend" : "Denied via frontend"
            })
        });
        
        const data = await response.json();
        
        // Hide consent panel
        consentPanel.classList.add('hidden');
        
        // Re-render with updated status
        displayResult(
            data.next_status || (approved ? 'complete' : 'blocked'),
            scanId,
            resultFilename.textContent,
            data.message || (approved ? 'Document approved and processed.' : 'Document denied and blocked.')
        );

    } catch (error) {
        console.error("Consent error:", error);
        resultMessage.textContent = 'Failed to submit consent. Is the server running?';
        approveBtn.disabled = false;
        denyBtn.disabled = false;
        approveBtn.textContent = '✅ Approve & Process';
        denyBtn.textContent = '🚫 Deny & Block';
    }
}

document.getElementById('consent-approve').addEventListener('click', () => handleConsent(true));
document.getElementById('consent-deny').addEventListener('click', () => handleConsent(false));
