class SubtitleNinja {
    constructor() {
        this.currentJobId = null;
        this.selectedFile = null;
        this.pollInterval = null;

        this.initializeElements();
        this.setupEventListeners();
    }

    initializeElements() {
        this.fileInput = document.getElementById('fileInput');
        this.uploadArea = document.querySelector('.upload-area');
        this.processBtn = document.getElementById('processBtn');
        this.fileInfo = document.getElementById('file-info');
        this.fileName = document.getElementById('file-name');
        this.fileSize = document.getElementById('file-size');

        this.styleSelector = document.getElementById('styleSelector');
        this.styleDescription = document.getElementById('styleDescription');

        this.uploadSection = document.getElementById('upload-section');
        this.progressSection = document.getElementById('progress-section');
        this.resultSection = document.getElementById('result-section');
        this.errorSection = document.getElementById('error-section');

        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.newVideoBtn = document.getElementById('newVideoBtn');
    }

    setupEventListeners() {
        // File input change
        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });

        // Process button
        this.processBtn.addEventListener('click', () => {
            this.processVideo();
        });

        // Download button
        this.downloadBtn.addEventListener('click', () => {
            this.downloadVideo();
        });

        // New video button
        this.newVideoBtn.addEventListener('click', () => {
            this.reset();
        });

        // Style selector change
        this.styleSelector.addEventListener('change', () => {
            this.updateStyleDescription();
        });
    }

    handleFileSelect(file) {
        if (!file) return;

        // Validate file type
        const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime',
                             'video/x-msvideo', 'video/x-matroska', 'video/webm', 'video/x-flv'];

        if (!allowedTypes.includes(file.type) && !this.isValidVideoExtension(file.name)) {
            this.showError('Please select a valid video file (MP4, AVI, MOV, MKV, WebM, FLV)');
            return;
        }

        this.selectedFile = file;
        this.fileName.textContent = file.name;
        this.fileSize.textContent = this.formatFileSize(file.size);
        this.fileInfo.style.display = 'block';
        this.processBtn.disabled = false;
        this.hideError();
    }

    isValidVideoExtension(filename) {
        const ext = filename.toLowerCase().split('.').pop();
        return ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'].includes(ext);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async processVideo() {
        if (!this.selectedFile) return;

        try {
            this.processBtn.disabled = true;
            this.processBtn.textContent = 'Uploading...';

            const formData = new FormData();
            formData.append('file', this.selectedFile);
            formData.append('style_preset', this.styleSelector.value);

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }

            const result = await response.json();
            this.currentJobId = result.job_id;

            this.showProgress();
            this.startProgressPolling();

        } catch (error) {
            console.error('Upload error:', error);
            this.showError(`Upload failed: ${error.message}`);
            this.processBtn.disabled = false;
            this.processBtn.textContent = 'Process Video';
        }
    }

    showProgress() {
        this.uploadSection.style.display = 'none';
        this.progressSection.style.display = 'block';
        this.hideError();
    }

    startProgressPolling() {
        this.pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/status/${this.currentJobId}`);
                if (!response.ok) throw new Error('Failed to get status');

                const status = await response.json();
                this.updateProgress(status);

                if (status.status === 'completed') {
                    this.showResult();
                    clearInterval(this.pollInterval);
                } else if (status.status === 'failed') {
                    this.showError(`Processing failed: ${status.error || 'Unknown error'}`);
                    clearInterval(this.pollInterval);
                    this.reset();
                }
            } catch (error) {
                console.error('Status polling error:', error);
                this.showError('Failed to get processing status');
                clearInterval(this.pollInterval);
                this.reset();
            }
        }, 2000); // Poll every 2 seconds
    }

    updateProgress(status) {
        const progress = status.progress || 0;
        this.progressFill.style.width = `${progress}%`;
        this.progressText.textContent = status.message || 'Processing...';
    }

    showResult() {
        this.progressSection.style.display = 'none';
        this.resultSection.style.display = 'block';
    }

    async downloadVideo() {
        if (!this.currentJobId) return;

        try {
            const response = await fetch(`/download/${this.currentJobId}`);
            if (!response.ok) throw new Error('Download failed');

            // Get filename from Content-Disposition header or use default
            let filename = `${this.selectedFile.name.split('.')[0]}_with_subtitles.mp4`;
            const contentDisposition = response.headers.get('content-disposition');
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download error:', error);
            this.showError(`Download failed: ${error.message}`);
        }
    }

    reset() {
        // Clear intervals
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }

        // Reset state
        this.currentJobId = null;
        this.selectedFile = null;

        // Reset UI
        this.fileInput.value = '';
        this.fileInfo.style.display = 'none';
        this.processBtn.disabled = true;
        this.processBtn.textContent = 'Process Video';

        // Show upload section, hide others
        this.uploadSection.style.display = 'block';
        this.progressSection.style.display = 'none';
        this.resultSection.style.display = 'none';
        this.hideError();

        // Reset progress
        this.progressFill.style.width = '0%';
        this.progressText.textContent = 'Initializing...';
    }

    showError(message) {
        this.errorSection.textContent = message;
        this.errorSection.style.display = 'block';
    }

    hideError() {
        this.errorSection.style.display = 'none';
    }

    updateStyleDescription() {
        const descriptions = {
            'instagram_classic': 'Best for: Professional content, tutorials',
            'tiktok_viral': 'Best for: Dance videos, trends, young audience',
            'youtube_professional': 'Best for: Educational content, business videos',
            'minimalist': 'Best for: Aesthetic content, quotes',
            'gaming': 'Best for: Gaming content, reactions'
        };

        this.styleDescription.textContent = descriptions[this.styleSelector.value] || '';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SubtitleNinja();
});