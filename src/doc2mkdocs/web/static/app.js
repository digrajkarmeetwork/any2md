// State management
let selectedFiles = [];
let currentJobId = null;

// DOM elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');
const convertBtn = document.getElementById('convert-btn');
const uploadSection = document.getElementById('upload-section');
const processingSection = document.getElementById('processing-section');
const resultsSection = document.getElementById('results-section');
const errorSection = document.getElementById('error-section');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const downloadBtn = document.getElementById('download-btn');
const newConversionBtn = document.getElementById('new-conversion-btn');
const retryBtn = document.getElementById('retry-btn');
const reportSummary = document.getElementById('report-summary');
const fileReports = document.getElementById('file-reports');
const errorMessage = document.getElementById('error-message');

// Event listeners
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', handleDragOver);
dropZone.addEventListener('dragleave', handleDragLeave);
dropZone.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
convertBtn.addEventListener('click', handleConvert);
downloadBtn.addEventListener('click', handleDownload);
newConversionBtn.addEventListener('click', resetUI);
retryBtn.addEventListener('click', resetUI);

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

// File management
async function addFiles(files) {
    for (const file of files) {
        // Check if file already added
        if (selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
            continue;
        }

        // Validate file
        const validation = await validateFile(file);
        
        selectedFiles.push({
            file: file,
            valid: validation.valid,
            error: validation.error
        });
    }

    renderFileList();
    updateConvertButton();
}

async function validateFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/validate', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        return {
            valid: data.valid,
            error: data.error
        };
    } catch (error) {
        return {
            valid: false,
            error: 'Validation failed'
        };
    }
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    renderFileList();
    updateConvertButton();
}

function renderFileList() {
    if (selectedFiles.length === 0) {
        fileList.innerHTML = '';
        return;
    }

    fileList.innerHTML = selectedFiles.map((item, index) => {
        const extension = item.file.name.split('.').pop().toLowerCase();
        const sizeKB = (item.file.size / 1024).toFixed(1);
        const sizeMB = (item.file.size / (1024 * 1024)).toFixed(2);
        const displaySize = item.file.size > 1024 * 1024 ? `${sizeMB} MB` : `${sizeKB} KB`;

        return `
            <div class="file-item">
                <div class="file-info">
                    <div class="file-icon ${extension}">${extension.toUpperCase()}</div>
                    <div class="file-details">
                        <div class="file-name">${item.file.name}</div>
                        <div class="file-size">${displaySize}</div>
                    </div>
                </div>
                <div class="file-status">
                    ${item.valid 
                        ? '<span class="status-badge valid">✓ Valid</span>'
                        : `<span class="status-badge invalid">✗ ${item.error}</span>`
                    }
                    <button class="remove-file" onclick="removeFile(${index})" title="Remove file">
                        ✕
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function updateConvertButton() {
    const hasValidFiles = selectedFiles.some(item => item.valid);
    convertBtn.disabled = !hasValidFiles;
}

// Conversion process
async function handleConvert() {
    const validFiles = selectedFiles.filter(item => item.valid).map(item => item.file);
    
    if (validFiles.length === 0) {
        return;
    }

    // Show processing section
    showSection('processing');

    // Upload files
    const formData = new FormData();
    validFiles.forEach(file => {
        formData.append('files', file);
    });

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const data = await response.json();
        currentJobId = data.job_id;

        // Poll for status
        pollStatus();

    } catch (error) {
        showError(error.message);
    }
}

async function pollStatus() {
    if (!currentJobId) return;

    try {
        const response = await fetch(`/api/status/${currentJobId}`);
        const data = await response.json();

        // Update progress
        updateProgress(data.progress);

        if (data.status === 'completed') {
            showResults(data.report);
        } else if (data.status === 'failed') {
            showError(data.error || 'Conversion failed');
        } else {
            // Continue polling
            setTimeout(pollStatus, 1000);
        }

    } catch (error) {
        showError('Failed to check conversion status');
    }
}

function updateProgress(progress) {
    progressFill.style.width = `${progress}%`;
    progressText.textContent = `${progress}%`;
}

// Results display
function showResults(report) {
    showSection('results');

    // Render summary
    const qualityClass = report.average_quality_score >= 0.8 ? 'high'
        : report.average_quality_score >= 0.5 ? 'medium' : 'low';

    reportSummary.innerHTML = `
        <h3>Conversion Summary</h3>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-value">${report.total_files}</div>
                <div class="summary-label">Total Files</div>
            </div>
            <div class="summary-item">
                <div class="summary-value" style="color: var(--success-color)">${report.successful}</div>
                <div class="summary-label">Successful</div>
            </div>
            <div class="summary-item">
                <div class="summary-value" style="color: var(--error-color)">${report.failed}</div>
                <div class="summary-label">Failed</div>
            </div>
            <div class="summary-item">
                <div class="summary-value quality-score ${qualityClass}">
                    ${(report.average_quality_score * 100).toFixed(0)}%
                </div>
                <div class="summary-label">Avg. Quality</div>
            </div>
        </div>
    `;

    // Render file reports
    fileReports.innerHTML = report.files.map(file => {
        const qualityScore = (file.quality_score * 100).toFixed(0);
        const qualityClass = file.quality_score >= 0.8 ? 'high'
            : file.quality_score >= 0.5 ? 'medium' : 'low';

        let warningsHtml = '';
        if (file.warnings && file.warnings.length > 0) {
            warningsHtml = `
                <div class="warnings-list">
                    <strong>Warnings:</strong>
                    <ul>
                        ${file.warnings.map(w => `<li>${w}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        let errorsHtml = '';
        if (file.errors && file.errors.length > 0) {
            errorsHtml = `
                <div class="errors-list">
                    <strong>Errors:</strong>
                    <ul>
                        ${file.errors.map(e => `<li>${e}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        return `
            <div class="file-report ${file.success ? '' : 'failed'}">
                <div class="file-report-header">
                    <span class="file-report-name">
                        ${file.success ? '✓' : '✗'} ${file.source_file}
                    </span>
                    <span class="quality-score ${qualityClass}">
                        Quality: ${qualityScore}%
                    </span>
                </div>
                ${file.output_file ? `<div style="font-size: 0.875rem; color: var(--text-secondary);">→ ${file.output_file}</div>` : ''}
                ${warningsHtml}
                ${errorsHtml}
            </div>
        `;
    }).join('');
}

// Download handler
async function handleDownload() {
    if (!currentJobId) return;

    try {
        const response = await fetch(`/api/download/${currentJobId}`);

        if (!response.ok) {
            throw new Error('Download failed');
        }

        // Create blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `doc2mkdocs-${currentJobId.substring(0, 8)}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        showError('Failed to download results');
    }
}

// Error handling
function showError(message) {
    showSection('error');
    errorMessage.textContent = message;
}

// UI helpers
function showSection(section) {
    uploadSection.classList.add('hidden');
    processingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');

    switch (section) {
        case 'upload':
            uploadSection.classList.remove('hidden');
            break;
        case 'processing':
            processingSection.classList.remove('hidden');
            break;
        case 'results':
            resultsSection.classList.remove('hidden');
            break;
        case 'error':
            errorSection.classList.remove('hidden');
            break;
    }
}

function resetUI() {
    selectedFiles = [];
    currentJobId = null;
    fileInput.value = '';
    renderFileList();
    updateConvertButton();
    updateProgress(0);
    showSection('upload');
}

// Initialize
showSection('upload');


