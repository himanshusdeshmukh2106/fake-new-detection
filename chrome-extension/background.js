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

  async factCheckFile(fileData, fileType) {
    if (!this.isConnected) {
      throw new Error('Backend service not available. Please ensure the fact-check server is running.');
    }

    try {
      // Validate file data
      if (!fileData || !fileData.base64Data) {
        throw new Error('Invalid file data received');
      }
      
      console.log('📋 File data validation:', {
        hasBase64Data: !!fileData.base64Data,
        base64Length: fileData.base64Data.length,
        fileName: fileData.name,
        fileType: fileData.type
      });
      
      // Convert base64 to blob
      const base64Data = fileData.base64Data;
      const base64Content = base64Data.split(',')[1]; // Remove data:image/png;base64, prefix
      
      if (!base64Content) {
        throw new Error('Invalid base64 data format');
      }
      
      // Convert base64 to binary
      const binaryString = atob(base64Content);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Create blob and file
      const blob = new Blob([bytes], { type: fileData.type });
      const file = new File([blob], fileData.name, { 
        type: fileData.type,
        lastModified: Date.now()
      });
      
      console.log('🔄 Reconstructed file:', {
        name: file.name,
        type: file.type,
        size: file.size,
        originalSize: fileData.size
      });
      
      // Validate reconstructed file
      if (file.size === 0) {
        throw new Error('File appears to be empty after reconstruction');
      }
      
      if (file.size !== fileData.size) {
        console.warn('⚠️ File size mismatch:', {
          original: fileData.size,
          reconstructed: file.size
        });
      }
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', fileType);

      console.log('📤 Sending file to backend:', {
        name: file.name,
        type: file.type,
        size: file.size,
        fileType: fileType
      });

      const response = await fetch(`${this.baseURL}/api/factcheck-file`, {
        method: 'POST',
        body: formData
      });

      console.log('📥 Backend response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error response:', errorText);
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('✅ File fact-check successful:', result);
      return result;
    } catch (error) {
      console.error('File fact-check API error:', error);
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
          console.log('📁 Processing file fact-check request');
          const fileResult = await factCheckAPI.factCheckFile(request.fileData, request.fileType);
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



        default:
          console.error('❌ Unknown action received:', request.action);
          console.error('❌ Available actions: factCheck, factCheckFile, testConnection, updateConfig, getConfig');
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