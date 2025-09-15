// Screen capture functionality for OpenFactVerification Chrome Extension
// Handles screen selection overlay and image capture

console.log('Screen capture script loaded');

class ScreenCapture {
  constructor() {
    this.isSelecting = false;
    this.selectionOverlay = null;
    this.startX = 0;
    this.startY = 0;
    this.endX = 0;
    this.endY = 0;
    this.currentSelection = null;
  }

  async startScreenSelection() {
    console.log('startScreenSelection called');
    if (this.isSelecting) {
      console.log('Already selecting, returning');
      return;
    }

    try {
      console.log('Requesting desktop capture permission');
      // Request desktop capture permission
      const response = await chrome.runtime.sendMessage({ action: 'captureScreen' });
      console.log('Desktop capture response:', response);
      
      if (!response.success) {
        throw new Error(response.error || 'Failed to start screen capture');
      }

      console.log('Creating selection overlay');
      // Create selection overlay
      this.createSelectionOverlay();
      this.isSelecting = true;
      
      // Show instructions
      this.showInstructions();
      
    } catch (error) {
      console.error('Error starting screen selection:', error);
      this.showError('Failed to start screen capture: ' + error.message);
    }
  }

  createSelectionOverlay() {
    // Remove existing overlay if any
    this.removeSelectionOverlay();

    // Create overlay container
    const overlay = document.createElement('div');
    overlay.id = 'factcheck-screen-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.3);
      z-index: 999999;
      cursor: crosshair;
      user-select: none;
    `;

    // Create selection rectangle
    const selectionRect = document.createElement('div');
    selectionRect.id = 'factcheck-selection-rect';
    selectionRect.style.cssText = `
      position: absolute;
      border: 2px dashed #007bff;
      background: rgba(0, 123, 255, 0.1);
      display: none;
      pointer-events: none;
    `;

    overlay.appendChild(selectionRect);
    document.body.appendChild(overlay);
    this.selectionOverlay = overlay;

    // Add event listeners
    overlay.addEventListener('mousedown', (e) => this.onMouseDown(e));
    overlay.addEventListener('mousemove', (e) => this.onMouseMove(e));
    overlay.addEventListener('mouseup', (e) => this.onMouseUp(e));
    overlay.addEventListener('keydown', (e) => this.onKeyDown(e));
    
    // Make overlay focusable for keyboard events
    overlay.tabIndex = -1;
    overlay.focus();
  }

  onMouseDown(e) {
    if (!this.isSelecting) return;
    
    this.startX = e.clientX;
    this.startY = e.clientY;
    this.endX = e.clientX;
    this.endY = e.clientY;
    
    const selectionRect = document.getElementById('factcheck-selection-rect');
    selectionRect.style.display = 'block';
    selectionRect.style.left = this.startX + 'px';
    selectionRect.style.top = this.startY + 'px';
    selectionRect.style.width = '0px';
    selectionRect.style.height = '0px';
  }

  onMouseMove(e) {
    if (!this.isSelecting) return;
    
    this.endX = e.clientX;
    this.endY = e.clientY;
    
    const selectionRect = document.getElementById('factcheck-selection-rect');
    if (selectionRect.style.display === 'block') {
      const left = Math.min(this.startX, this.endX);
      const top = Math.min(this.startY, this.endY);
      const width = Math.abs(this.endX - this.startX);
      const height = Math.abs(this.endY - this.startY);
      
      selectionRect.style.left = left + 'px';
      selectionRect.style.top = top + 'px';
      selectionRect.style.width = width + 'px';
      selectionRect.style.height = height + 'px';
    }
  }

  async onMouseUp(e) {
    if (!this.isSelecting) return;
    
    const width = Math.abs(this.endX - this.startX);
    const height = Math.abs(this.endY - this.startY);
    
    // Minimum selection size
    if (width < 10 || height < 10) {
      this.showError('Please select a larger area');
      return;
    }

    // Calculate selection bounds
    const left = Math.min(this.startX, this.endX);
    const top = Math.min(this.startY, this.endY);
    
    this.currentSelection = {
      x: left,
      y: top,
      width: width,
      height: height
    };

    // Show confirmation dialog
    this.showConfirmationDialog();
  }

  onKeyDown(e) {
    if (e.key === 'Escape') {
      this.cancelSelection();
    }
  }

  showInstructions() {
    const instructions = document.createElement('div');
    instructions.id = 'factcheck-instructions';
    instructions.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: #007bff;
      color: white;
      padding: 12px 20px;
      border-radius: 6px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      z-index: 1000000;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    instructions.innerHTML = `
      📷 Click and drag to select an area for fact-checking • Press ESC to cancel
    `;
    
    document.body.appendChild(instructions);
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
      if (instructions.parentNode) {
        instructions.remove();
      }
    }, 3000);
  }

  showConfirmationDialog() {
    const dialog = document.createElement('div');
    dialog.id = 'factcheck-confirmation';
    dialog.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      z-index: 1000001;
      text-align: center;
      min-width: 300px;
    `;
    
    dialog.innerHTML = `
      <h3 style="margin: 0 0 12px 0; color: #333;">Capture Selected Area?</h3>
      <p style="margin: 0 0 20px 0; color: #666; font-size: 14px;">
        This will capture the selected screen area and analyze it for factual claims.
      </p>
      <div style="display: flex; gap: 12px; justify-content: center;">
        <button id="factcheck-capture-btn" style="
          background: #007bff;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        ">📷 Capture & Analyze</button>
        <button id="factcheck-cancel-btn" style="
          background: #6c757d;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        ">Cancel</button>
      </div>
    `;
    
    document.body.appendChild(dialog);
    
    // Add event listeners
    document.getElementById('factcheck-capture-btn').addEventListener('click', () => {
      dialog.remove();
      this.captureSelection();
    });
    
    document.getElementById('factcheck-cancel-btn').addEventListener('click', () => {
      dialog.remove();
      this.cancelSelection();
    });
  }

  async captureSelection() {
    try {
      this.showProcessingIndicator();
      
      // Request screen capture using Chrome's desktop capture API
      const response = await chrome.runtime.sendMessage({ action: 'captureScreen' });
      
      if (!response.success) {
        throw new Error(response.error);
      }
      
      // Use the stream ID to capture the screen
      const canvas = await this.captureScreenWithStreamId(response.streamId);
      
      // Convert canvas to base64 image data
      const imageData = canvas.toDataURL('image/png');
      
      // Send to background script for processing
      const processResponse = await chrome.runtime.sendMessage({
        action: 'processScreenshot',
        imageData: imageData
      });
      
      this.removeSelectionOverlay();
      
      if (processResponse.success) {
        this.showResults(processResponse.data);
      } else {
        this.showError(processResponse.error || 'Failed to process screenshot');
      }
      
    } catch (error) {
      console.error('Error capturing selection:', error);
      this.showError('Failed to capture screen area: ' + error.message);
      this.removeSelectionOverlay();
    }
  }

  async captureScreenWithStreamId(streamId) {
    return new Promise((resolve, reject) => {
      // Create video element to capture stream
      const video = document.createElement('video');
      video.style.position = 'absolute';
      video.style.top = '-9999px';
      video.style.left = '-9999px';
      document.body.appendChild(video);
      
      // Get media stream using the stream ID
      navigator.mediaDevices.getUserMedia({
        video: {
          mandatory: {
            chromeMediaSource: 'desktop',
            chromeMediaSourceId: streamId,
            maxWidth: screen.width,
            maxHeight: screen.height
          }
        }
      }).then(stream => {
        video.srcObject = stream;
        video.play();
        
        video.addEventListener('loadedmetadata', () => {
          // Create canvas for the selected area
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          
          canvas.width = this.currentSelection.width;
          canvas.height = this.currentSelection.height;
          
          // Wait for video to be ready
          setTimeout(() => {
            try {
              // Calculate scale factor
              const scaleX = video.videoWidth / screen.width;
              const scaleY = video.videoHeight / screen.height;
              
              // Draw the selected portion to canvas
              ctx.drawImage(
                video,
                this.currentSelection.x * scaleX,
                this.currentSelection.y * scaleY,
                this.currentSelection.width * scaleX,
                this.currentSelection.height * scaleY,
                0, 0,
                this.currentSelection.width,
                this.currentSelection.height
              );
              
              // Stop the stream and cleanup
              stream.getTracks().forEach(track => track.stop());
              document.body.removeChild(video);
              
              resolve(canvas);
            } catch (drawError) {
              stream.getTracks().forEach(track => track.stop());
              document.body.removeChild(video);
              reject(drawError);
            }
          }, 100);
        });
        
        video.addEventListener('error', (error) => {
          stream.getTracks().forEach(track => track.stop());
          document.body.removeChild(video);
          reject(error);
        });
        
      }).catch(error => {
        document.body.removeChild(video);
        reject(error);
      });
    });
  }

  showProcessingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'factcheck-processing';
    indicator.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      z-index: 1000001;
      text-align: center;
    `;
    
    indicator.innerHTML = `
      <div style="margin-bottom: 12px;">
        <div style="
          width: 24px;
          height: 24px;
          border: 3px solid #f3f3f3;
          border-top: 3px solid #007bff;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto;
        "></div>
      </div>
      <p style="margin: 0; color: #333;">Processing screenshot...</p>
    `;
    
    // Add CSS animation
    if (!document.getElementById('factcheck-spin-style')) {
      const style = document.createElement('style');
      style.id = 'factcheck-spin-style';
      style.textContent = `
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `;
      document.head.appendChild(style);
    }
    
    document.body.appendChild(indicator);
  }

  showResults(results) {
    // Remove processing indicator
    const processing = document.getElementById('factcheck-processing');
    if (processing) processing.remove();
    
    // Show results in a modal (reuse existing modal functionality)
    if (window.factCheckContentScript) {
      window.factCheckContentScript.displayResultsInModal(results);
    } else {
      // Fallback: show simple results
      this.showSimpleResults(results);
    }
  }

  showSimpleResults(results) {
    const modal = document.createElement('div');
    modal.id = 'factcheck-results-modal';
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.5);
      z-index: 1000001;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;
    
    const summary = results.summary || {};
    const claims = results.claim_detail || [];
    
    modal.innerHTML = `
      <div style="
        background: white;
        padding: 24px;
        border-radius: 8px;
        max-width: 500px;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
          <h3 style="margin: 0; color: #333;">📊 Fact Check Results</h3>
          <button onclick="this.closest('#factcheck-results-modal').remove()" style="
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: #666;
          ">&times;</button>
        </div>
        
        <div style="text-align: center; margin-bottom: 20px;">
          <div style="font-size: 32px; font-weight: bold; color: #007bff; margin-bottom: 8px;">
            ${(summary.factuality * 100).toFixed(1)}%
          </div>
          <div style="color: #666; font-size: 14px;">Overall Factuality</div>
        </div>
        
        <div style="margin-bottom: 20px;">
          <strong>Claims Found:</strong> ${claims.length}<br>
          <strong>Supported:</strong> ${summary.num_supported_claims || 0}<br>
          <strong>Refuted:</strong> ${summary.num_refuted_claims || 0}<br>
          <strong>Controversial:</strong> ${summary.num_controversial_claims || 0}
        </div>
        
        ${claims.length > 0 ? `
          <div>
            <h4 style="margin: 0 0 12px 0; color: #333;">Individual Claims:</h4>
            ${claims.map(claim => `
              <div style="
                padding: 12px;
                margin-bottom: 8px;
                border-radius: 4px;
                background: ${this.getClaimBackgroundColor(claim.factuality)};
                border-left: 4px solid ${this.getClaimBorderColor(claim.factuality)};
              ">
                <div style="font-weight: 500; margin-bottom: 4px;">
                  ${this.getFactualityText(claim.factuality)}
                </div>
                <div style="font-size: 14px; color: #555;">
                  "${claim.claim}"
                </div>
              </div>
            `).join('')}
          </div>
        ` : '<p style="text-align: center; color: #666;">No verifiable claims found in the selected area.</p>'}
      </div>
    `;
    
    document.body.appendChild(modal);
  }

  getClaimBackgroundColor(factuality) {
    if (typeof factuality === 'string') return '#f8f9fa';
    if (factuality >= 0.8) return '#d4edda';
    if (factuality >= 0.5) return '#fff3cd';
    return '#f8d7da';
  }

  getClaimBorderColor(factuality) {
    if (typeof factuality === 'string') return '#6c757d';
    if (factuality >= 0.8) return '#28a745';
    if (factuality >= 0.5) return '#ffc107';
    return '#dc3545';
  }

  getFactualityText(factuality) {
    if (typeof factuality === 'string') return 'Not Checked';
    if (factuality >= 0.8) return '✅ Supported';
    if (factuality >= 0.5) return '⚠️ Controversial';
    return '❌ Refuted';
  }

  showError(message) {
    this.removeSelectionOverlay();
    
    const error = document.createElement('div');
    error.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #dc3545;
      color: white;
      padding: 12px 20px;
      border-radius: 6px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      z-index: 1000000;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    error.textContent = message;
    
    document.body.appendChild(error);
    
    setTimeout(() => {
      if (error.parentNode) {
        error.remove();
      }
    }, 5000);
  }

  cancelSelection() {
    this.removeSelectionOverlay();
  }

  removeSelectionOverlay() {
    this.isSelecting = false;
    
    // Remove overlay
    if (this.selectionOverlay) {
      this.selectionOverlay.remove();
      this.selectionOverlay = null;
    }
    
    // Remove instructions
    const instructions = document.getElementById('factcheck-instructions');
    if (instructions) instructions.remove();
    
    // Remove confirmation dialog
    const confirmation = document.getElementById('factcheck-confirmation');
    if (confirmation) confirmation.remove();
    
    // Remove processing indicator
    const processing = document.getElementById('factcheck-processing');
    if (processing) processing.remove();
  }
}

// Initialize screen capture functionality
console.log('Initializing screen capture');
const screenCapture = new ScreenCapture();
console.log('Screen capture initialized');

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Screen capture received message:', request);
  if (request.action === 'startScreenSelection') {
    console.log('Starting screen selection');
    screenCapture.startScreenSelection();
    sendResponse({ success: true });
  }
});