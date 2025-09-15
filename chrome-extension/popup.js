// OpenFactVerification Chrome Extension Popup JavaScript
// Matches the main Python application UI design

class FactCheckPopup {
  constructor() {
    this.currentTab = 'text';
    this.currentResults = null;
    this.isProcessing = false;
    this.selectedFile = null;
    this.elapsedTimer = null;
    
    this.init();
  }

  async init() {
    this.setupEventListeners();
    this.setupTabSwitching();
    this.checkConnectionStatus();
    this.loadPastedTextIfAvailable();
  }

  setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
      button.addEventListener('click', () => this.switchTab(button.dataset.tab));
    });

    // Text input actions
    document.getElementById('factCheckTextButton').addEventListener('click', () => this.factCheckText());

    // File input actions
    document.getElementById('imageUploadBtn').addEventListener('click', () => document.getElementById('fileInput').click());
    document.getElementById('videoUploadBtn').addEventListener('click', () => document.getElementById('fileInput').click());
    document.getElementById('screenCaptureBtn').addEventListener('click', () => this.initScreenCapture());
    document.getElementById('fileInput').addEventListener('change', (e) => this.handleFileSelect(e));
    document.getElementById('clearFileBtn').addEventListener('click', () => this.clearFile());
    document.getElementById('factCheckFileButton').addEventListener('click', () => this.factCheckFile());

    // Results actions
    document.getElementById('copyResultsButton').addEventListener('click', () => this.copyResults());
    document.getElementById('clearResultsButton').addEventListener('click', () => this.clearResults());
    document.getElementById('retryButton').addEventListener('click', () => this.retryLastAction());

    // Settings and navigation
    document.getElementById('settingsLink').addEventListener('click', () => this.openSettings());
    document.getElementById('helpLink').addEventListener('click', () => this.showHelp());

    // Auto-resize textarea
    const textInput = document.getElementById('textInput');
    textInput.addEventListener('input', () => this.autoResizeTextarea(textInput));
  }

  setupTabSwitching() {
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });
    document.getElementById('textTab').classList.add('active');
  }

  switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
      button.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');

    this.currentTab = tabName;
  }

  async checkConnectionStatus() {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');

    try {
      const response = await chrome.runtime.sendMessage({ action: 'testConnection' });
      
      if (response.success && response.connected) {
        statusDot.className = 'status-dot connected';
        statusText.textContent = 'Connected';
      } else {
        statusDot.className = 'status-dot disconnected';
        statusText.textContent = 'Disconnected';
      }
    } catch (error) {
      statusDot.className = 'status-dot disconnected';
      statusText.textContent = 'Error';
    }
  }

  async loadPastedTextIfAvailable() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => window.getSelection().toString().trim()
      });
      
      if (results[0]?.result) {
        document.getElementById('textInput').value = results[0].result;
        this.autoResizeTextarea(document.getElementById('textInput'));
      }
    } catch (error) {
      // Ignore errors - user might be on a restricted page
    }
  }

  autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  }

  handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
      this.processSelectedFile(files[0]);
    }
  }

  processSelectedFile(file) {
    const validTypes = ['image/', 'video/'];
    if (!validTypes.some(type => file.type.startsWith(type))) {
      this.showError('Please select an image or video file.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      this.showError('File size must be less than 10MB.');
      return;
    }

    this.selectedFile = file;
    
    const filePreview = document.getElementById('filePreview');
    const fileName = document.getElementById('fileName');
    const factCheckFileButton = document.getElementById('factCheckFileButton');
    
    fileName.textContent = `📁 ${file.name} (${this.formatFileSize(file.size)})`;
    filePreview.style.display = 'block';
    factCheckFileButton.disabled = false;
  }

  clearFile() {
    this.selectedFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('filePreview').style.display = 'none';
    document.getElementById('factCheckFileButton').disabled = true;
  }

  async initScreenCapture() {
    console.log('📷 Screen capture button clicked');
    
    // First test if background script is responding
    try {
      console.log('🔍 Testing background script connection...');
      const testResponse = await chrome.runtime.sendMessage({ action: 'testConnection' });
      console.log('🔍 Test response:', testResponse);
    } catch (testError) {
      console.error('❌ Background script test failed:', testError);
    }
    
    try {
      console.log('📷 Sending startScreenCapture message to background script');
      const response = await chrome.runtime.sendMessage({ action: 'startScreenCapture' });
      console.log('📷 Response from background script:', response);
      
      if (response && response.success) {
        console.log('Screen capture initiated successfully, closing popup');
        // Screen capture initiated successfully - the content script will handle the selection
        window.close(); // Close popup to allow screen selection
      } else {
        const errorMsg = response ? response.error : 'No response from background script';
        console.error('Screen capture failed:', errorMsg);
        this.showError(errorMsg || 'Failed to start screen capture');
      }
    } catch (error) {
      console.error('Error in initScreenCapture:', error);
      this.showError('Error starting screen capture: ' + error.message);
    }
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  async factCheckText() {
    const text = document.getElementById('textInput').value.trim();
    if (!text) {
      this.showError('Please enter text to fact-check.');
      return;
    }

    this.showLoading();
    this.lastAction = () => this.factCheckText();

    try {
      const response = await chrome.runtime.sendMessage({
        action: 'factCheck',
        text: text
      });
      
      if (response && response.success) {
        const actualData = response.data.data || response.data;
        this.displayResults(actualData);
      } else {
        const errorMsg = response ? response.error : 'No response from background script';
        this.showError(errorMsg || 'Failed to fact-check text');
      }
    } catch (error) {
      console.error('Error in factCheckText:', error);
      this.showError('Error during fact-checking: ' + error.message);
    }
  }

  async factCheckFile() {
    if (!this.selectedFile) {
      this.showError('Please select a file first.');
      return;
    }

    this.showLoading();
    this.lastAction = () => this.factCheckFile();

    try {
      const fileType = this.selectedFile.type.startsWith('image/') ? 'image' : 'video';
      
      const response = await chrome.runtime.sendMessage({
        action: 'factCheckFile',
        file: this.selectedFile,
        fileType: fileType
      });

      if (response && response.success) {
        const actualData = response.data.data || response.data;
        this.displayResults(actualData);
      } else {
        const errorMsg = response ? response.error : 'No response from background script';
        this.showError(errorMsg || 'Failed to fact-check file');
      }
    } catch (error) {
      console.error('Error in factCheckFile:', error);
      this.showError('Error during file fact-checking: ' + error.message);
    }
  }

  showLoading() {
    this.isProcessing = true;
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('loadingState').style.display = 'block';
    document.getElementById('resultsDisplay').style.display = 'none';
    document.getElementById('errorState').style.display = 'none';

    this.startElapsedTimer();
  }

  startElapsedTimer() {
    let seconds = 0;
    const elapsedTimeElement = document.getElementById('elapsedTime');
    
    this.elapsedTimer = setInterval(() => {
      seconds++;
      elapsedTimeElement.textContent = seconds;
    }, 1000);
  }

  stopElapsedTimer() {
    if (this.elapsedTimer) {
      clearInterval(this.elapsedTimer);
      this.elapsedTimer = null;
    }
  }

  displayResults(results) {
    this.isProcessing = false;
    this.currentResults = results;
    this.stopElapsedTimer();

    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('resultsDisplay').style.display = 'block';
    document.getElementById('errorState').style.display = 'none';

    if (!results || typeof results !== 'object') {
      this.showError('Invalid results format received');
      return;
    }

    // Calculate actual metrics from claim data for consistency
    const claims = results.claim_detail || [];
    let actualSupportedCount = 0;
    let actualRefutedCount = 0;
    let actualControversialCount = 0;
    
    claims.forEach(claim => {
      if (claim && typeof claim.factuality !== 'undefined') {
        const category = this.getFactualityCategory(claim.factuality);
        if (category === 'supported') actualSupportedCount++;
        else if (category === 'refuted') actualRefutedCount++;
        else if (category === 'controversial') actualControversialCount++;
      }
    });

    // Update metrics bar with actual calculated values
    const summary = results.summary || {};
    const factuality = summary.factuality || 0;
    
    document.getElementById('overallCredibility').textContent = (factuality * 100).toFixed(1) + '%';
    document.getElementById('totalClaims').textContent = claims.length;
    document.getElementById('supportedClaims').textContent = actualSupportedCount;
    document.getElementById('refutedClaims').textContent = actualRefutedCount;
    document.getElementById('controversialClaims').textContent = actualControversialCount;

    // Display claims
    this.renderClaims(claims);
  }

  renderClaims(claims) {
    const claimsList = document.getElementById('claimsList');
    
    if (!claims || !Array.isArray(claims) || claims.length === 0) {
      claimsList.innerHTML = '<p style="text-align: center; color: #6c757d; font-size: 13px;">No claims found to verify.</p>';
      return;
    }

    claimsList.innerHTML = claims.map((claim, index) => {
      if (!claim) return '';
      
      const category = this.getFactualityCategory(claim.factuality);
      const statusText = this.getFactualityText(claim.factuality);
      const evidenceCount = (claim.evidences && Array.isArray(claim.evidences)) ? claim.evidences.length : 0;
      const claimText = claim.claim || 'No claim text available';
      
      return `
        <div class="claim-item ${category}">
          <div class="claim-status-badge">
            Claim ${index + 1}: ${statusText}
          </div>
          <div class="claim-text">${claimText}</div>
          <div class="claim-evidence-count">${evidenceCount} evidence(s) found</div>
        </div>
      `;
    }).filter(html => html !== '').join('');
  }

  getFactualityCategory(factuality) {
    if (typeof factuality === 'string') return 'not-checked';
    if (factuality >= 0.8) return 'supported';
    if (factuality >= 0.5) return 'controversial';
    return 'refuted';
  }

  getFactualityText(factuality) {
    if (typeof factuality === 'string') return 'Not Checked';
    if (factuality >= 0.8) return 'SUPPORTED';
    if (factuality >= 0.5) return 'CONTROVERSIAL';
    return 'REFUTED';
  }

  showError(message) {
    this.isProcessing = false;
    this.stopElapsedTimer();
    
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('resultsDisplay').style.display = 'none';
    document.getElementById('errorState').style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
  }

  async copyResults() {
    if (!this.currentResults) return;

    const summary = this.currentResults.summary || {};
    const claims = this.currentResults.claim_detail || [];
    
    let report = `OpenFactVerification Report\n`;
    report += `================================\n\n`;
    report += `Overall Factuality: ${(summary.factuality * 100).toFixed(1)}%\n`;
    report += `Total Claims: ${claims.length}\n`;
    report += `Supported: ${this.currentResults.summary?.num_supported_claims || 0}\n`;
    report += `Refuted: ${this.currentResults.summary?.num_refuted_claims || 0}\n`;
    report += `Controversial: ${this.currentResults.summary?.num_controversial_claims || 0}\n\n`;
    
    if (claims.length > 0) {
      report += `Claims Analysis:\n`;
      report += `----------------\n\n`;
      
      claims.forEach((claim, index) => {
        report += `${index + 1}. "${claim.claim}"\n`;
        report += `   Status: ${this.getFactualityText(claim.factuality)}\n`;
        if (claim.evidences && claim.evidences.length > 0) {
          report += `   Evidence Found: ${claim.evidences.length} sources\n`;
        }
        report += `\n`;
      });
    }

    try {
      await navigator.clipboard.writeText(report);
      const button = document.getElementById('copyResultsButton');
      const originalText = button.textContent;
      button.textContent = '✓ Copied!';
      setTimeout(() => {
        button.textContent = originalText;
      }, 2000);
    } catch (error) {
      console.error('Failed to copy results:', error);
    }
  }

  clearResults() {
    this.currentResults = null;
    this.stopElapsedTimer();
    document.getElementById('resultsSection').style.display = 'none';
    
    // Reset metrics
    document.getElementById('overallCredibility').textContent = '--';
    document.getElementById('totalClaims').textContent = '--';
    document.getElementById('supportedClaims').textContent = '--';
    document.getElementById('refutedClaims').textContent = '--';
    document.getElementById('controversialClaims').textContent = '--';
    
    // Clear inputs
    document.getElementById('textInput').value = '';
    this.clearFile();
  }

  retryLastAction() {
    if (this.lastAction) {
      this.lastAction();
    }
  }

  openSettings() {
    chrome.runtime.openOptionsPage();
  }

  showHelp() {
    const helpWindow = window.open('', '_blank', 'width=600,height=500');
    helpWindow.document.write(`
      <html>
        <head><title>OpenFactVerification Help</title></head>
        <body style="font-family: system-ui; padding: 20px; line-height: 1.6;">
          <h2>How to Use OpenFactVerification</h2>
          
          <h3>Getting Started</h3>
          <p>1. Make sure the backend server is running (localhost:2024)</p>
          <p>2. Configure your API keys in Settings</p>
          
          <h3>Text Fact-Checking</h3>
          <p>• Enter or paste text in the Text tab</p>
          <p>• Click "Check Facts" to analyze</p>
          
          <h3>File Analysis</h3>
          <p>• Upload images or videos in the Media tab</p>
          <p>• Supports common image and video formats</p>
          
          <h3>Understanding Results</h3>
          <p>• <span style="color: #28a745;">Green</span>: Supported claims</p>
          <p>• <span style="color: #dc3545;">Red</span>: Refuted claims</p>
          <p>• <span style="color: #ffc107;">Yellow</span>: Controversial claims</p>
          
          <h3>Troubleshooting</h3>
          <p>• Ensure backend server is running on localhost:2024</p>
          <p>• Check your API keys in Settings</p>
          <p>• Some pages may be restricted for analysis</p>
        </body>
      </html>
    `);
  }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new FactCheckPopup();
});