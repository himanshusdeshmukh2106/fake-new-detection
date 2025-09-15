// Background service worker for OpenFactVerification Chrome Extension
// Handles API communication and manages extension lifecycle

class FactCheckAPI {
  constructor() {
    this.baseURL = 'http://localhost:2024'; // Default backend URL
    this.isConnected = false;
  }

  async init() {
    // Get stored API configuration
    const config = await this.getStoredConfig();
    if (config.backendURL) {
      this.baseURL = config.backendURL;
    }
    
    // Test connection to backend
    await this.testConnection();
  }

  async getStoredConfig() {
    return new Promise((resolve) => {
      chrome.storage.sync.get(['apiConfig'], (result) => {
        resolve(result.apiConfig || {
          backendURL: 'http://localhost:2024',
          geminiApiKey: '',
          serperApiKey: ''
        });
      });
    });
  }

  async testConnection() {
    try {
      const response = await fetch(`${this.baseURL}/health`, { 
        method: 'GET'
      });
      this.isConnected = response.ok;
      return this.isConnected;
    } catch (error) {
      console.error('Backend connection failed:', error);
      this.isConnected = false;
      return false;
    }
  }

  async factCheck(text) {
    if (!this.isConnected) {
      throw new Error('Backend service not available. Please ensure the fact-check server is running.');
    }

    try {
      const response = await fetch(`${this.baseURL}/api/factcheck`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          type: 'text'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Backend API returned:', result);
      console.log('Result type:', typeof result);
      console.log('Result keys:', Object.keys(result || {}));
      return result;
    } catch (error) {
      console.error('Fact-check API error:', error);
      throw error;
    }
  }

  async factCheckFile(file, fileType) {
    if (!this.isConnected) {
      throw new Error('Backend service not available. Please ensure the fact-check server is running.');
    }

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', fileType);

      const response = await fetch(`${this.baseURL}/api/factcheck-file`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('File fact-check API error:', error);
      throw error;
    }
  }

  async factCheckScreenshot(imageData) {
    if (!this.isConnected) {
      throw new Error('Backend service not available. Please ensure the fact-check server is running.');
    }

    try {
      // Convert base64 image data to blob
      const base64Data = imageData.split(',')[1]; // Remove data:image/png;base64, prefix
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'image/png' });
      
      // Create file from blob
      const file = new File([blob], 'screenshot.png', { type: 'image/png' });
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', 'image');

      const response = await fetch(`${this.baseURL}/api/factcheck-file`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Screenshot fact-check API error:', error);
      throw error;
    }
  }
}

// Initialize API instance
const factCheckAPI = new FactCheckAPI();

// Extension lifecycle
chrome.runtime.onStartup.addListener(() => {
  factCheckAPI.init();
});

chrome.runtime.onInstalled.addListener(() => {
  factCheckAPI.init();
  
  // Set default configuration
  chrome.storage.sync.set({
    apiConfig: {
      backendURL: 'http://localhost:2024',
      geminiApiKey: '',
      serperApiKey: ''
    }
  });
  
  // Create context menu for selected text
  chrome.contextMenus.create({
    id: "factcheck-selection",
    title: "Fact-check selected text",
    contexts: ["selection"]
  });
});

// Message handling from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('🔍 Background script received message:', request);
  console.log('🔍 Sender info:', sender);
  const handleAsync = async () => {
    try {
      console.log('🔍 Processing action:', request.action);
      switch (request.action) {
        case 'factCheck':
          const result = await factCheckAPI.factCheck(request.text);
          return { success: true, data: result };

        case 'factCheckFile':
          const fileResult = await factCheckAPI.factCheckFile(request.file, request.fileType);
          return { success: true, data: fileResult };

        case 'testConnection':
          const isConnected = await factCheckAPI.testConnection();
          return { success: true, connected: isConnected };

        case 'updateConfig':
          await chrome.storage.sync.set({ apiConfig: request.config });
          factCheckAPI.baseURL = request.config.backendURL;
          await factCheckAPI.testConnection();
          return { success: true };

        case 'getConfig':
          const config = await factCheckAPI.getStoredConfig();
          return { success: true, config: config };

        case 'startScreenCapture':
          console.log('✅ startScreenCapture case reached!');
          try {
            console.log('startScreenCapture: Getting active tab');
            // Request desktop capture permission and start screen selection
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            console.log('startScreenCapture: Active tab found:', tab.id, tab.url);
            
            // Check if tab is restricted
            if (tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://') || tab.url.startsWith('edge://') || tab.url.startsWith('about:')) {
              console.error('Cannot inject script into restricted page:', tab.url);
              return { success: false, error: 'Cannot capture screen on this page. Please navigate to a regular website.' };
            }
            
            // Send message to content script to start screen selection
            // (content.js is already injected via manifest)
            console.log('startScreenCapture: Sending startScreenSelection message');
            const messageResponse = await chrome.tabs.sendMessage(tab.id, {
              action: 'startScreenSelection'
            });
            console.log('startScreenCapture: Message response:', messageResponse);
            
            return { success: true };
          } catch (error) {
            console.error('Screen capture error:', error);
            // Provide more specific error messages
            let errorMessage = error.message;
            if (error.message.includes('Cannot access')) {
              errorMessage = 'Cannot capture screen on this page. Please try on a regular website.';
            } else if (error.message.includes('Extension context invalidated')) {
              errorMessage = 'Extension needs to be reloaded. Please reload the extension and try again.';
            } else if (error.message.includes('Could not establish connection')) {
              errorMessage = 'Page not ready. Please refresh the page and try again.';
            }
            return { success: false, error: errorMessage };
          }

        case 'captureScreen':
          try {
            // Request screen capture
            const streamId = await new Promise((resolve, reject) => {
              chrome.desktopCapture.chooseDesktopMedia(
                ['screen', 'window', 'tab'],
                sender.tab,
                (streamId) => {
                  if (streamId) {
                    resolve(streamId);
                  } else {
                    reject(new Error('Screen capture was cancelled'));
                  }
                }
              );
            });
            
            return { success: true, streamId: streamId };
          } catch (error) {
            console.error('Desktop capture error:', error);
            return { success: false, error: error.message };
          }

        case 'processScreenshot':
          try {
            // Process the captured screenshot like an image file
            const result = await factCheckAPI.factCheckScreenshot(request.imageData);
            return { success: true, data: result };
          } catch (error) {
            console.error('Screenshot processing error:', error);
            return { success: false, error: error.message };
          }

        default:
          console.error('❌ Unknown action received:', request.action);
          console.error('❌ Available actions: factCheck, factCheckFile, testConnection, updateConfig, getConfig, startScreenCapture, captureScreen, processScreenshot');
          return { success: false, error: 'Unknown action: ' + request.action };
      }
    } catch (error) {
      console.error('Background script error:', error);
      return { success: false, error: error.message };
    }
  };

  // Handle async operations
  handleAsync().then(sendResponse);
  return true; // Keep message channel open for async response
});

// Context menu click handler
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "factcheck-selection" && info.selectionText) {
    // Send message to content script to show fact-check modal
    chrome.tabs.sendMessage(tab.id, {
      action: "showFactCheckModal",
      text: info.selectionText
    });
  }
});

// Badge management
function updateBadge(tabId, factCheckResults) {
  if (factCheckResults && factCheckResults.summary) {
    const factuality = factCheckResults.summary.factuality;
    let badgeText = '';
    let badgeColor = '#666666';

    if (factuality >= 0.8) {
      badgeText = '✓';
      badgeColor = '#28a745';
    } else if (factuality >= 0.5) {
      badgeText = '?';
      badgeColor = '#ffc107';
    } else if (factuality > 0) {
      badgeText = '!';
      badgeColor = '#dc3545';
    }

    chrome.action.setBadgeText({ text: badgeText, tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: badgeColor, tabId: tabId });
  }
}

// Clear badge when tab changes
chrome.tabs.onActivated.addListener((activeInfo) => {
  chrome.action.setBadgeText({ text: '', tabId: activeInfo.tabId });
});