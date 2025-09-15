# OpenFactVerification Chrome Extension

Convert your OpenFactVerification project into a powerful Chrome extension for real-time fact-checking on any website!

## 🌟 Features

- **Real-time Fact Checking**: Verify claims on any webpage instantly
- **Multiple Input Methods**: Text, images, videos, and full page analysis
- **Smart Text Selection**: Double-click any text to fact-check quickly
- **Visual Claim Highlighting**: See fact-checked claims highlighted on pages
- **Comprehensive Results**: Detailed factuality scores and evidence links
- **Secure Configuration**: Encrypted API key storage and secure backend communication

## 📋 Prerequisites

Before installing the extension, ensure you have:

1. **Python 3.9+** installed on your system
2. **OpenFactVerification project** set up (this directory)
3. **API Keys**:
   - **Gemini API Key** (required) - [Get it here](https://makersuite.google.com/app/apikey)
   - **Serper API Key** (optional) - [Get it here](https://serper.dev/)

## 🚀 Quick Setup

### Step 1: Install Backend Dependencies

```bash
# Install additional dependencies for the extension backend
pip install -r extension_requirements.txt

# Ensure all main dependencies are installed
pip install -r requirements.txt
```

### Step 2: Configure API Keys

Create or update your `api_config.yaml` file:

```yaml
GEMINI_API_KEY: "your_gemini_api_key_here"
SERPER_API_KEY: "your_serper_api_key_here"  # Optional
```

Or set environment variables:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
export SERPER_API_KEY="your_serper_api_key_here"  # Optional
```

### Step 3: Start the Backend Server

```bash
# Start the extension backend server
python extension_backend.py

# The server will run on http://localhost:2024
# Keep this running while using the extension
```

### Step 4: Install the Chrome Extension

1. **Open Chrome** and navigate to `chrome://extensions/`
2. **Enable Developer Mode** (toggle in the top-right corner)
3. **Click "Load unpacked"**
4. **Select the `chrome-extension` folder** in this directory
5. The extension will be installed and ready to use!

## ⚙️ Configuration

### First-time Setup

1. **Click the extension icon** in Chrome's toolbar
2. **Click "Settings"** in the popup footer
3. **Configure your API keys** in the settings page
4. **Test the connection** to ensure everything works

### Backend Configuration

The backend server supports various configuration options:

```bash
# Custom host and port
python extension_backend.py --host 0.0.0.0 --port 3000

# Custom config file
python extension_backend.py --config my_config.yaml

# Debug mode
python extension_backend.py --debug
```

## 🎯 How to Use

### Text Fact-Checking

1. **Select any text** on a webpage
2. **Double-click** to show the quick fact-check button
3. **Click the button** or right-click and select "Fact-check selected text"
4. **View results** in the modal that appears

### Extension Popup

1. **Click the extension icon** in Chrome's toolbar
2. **Choose your input method**:
   - **Text**: Paste or type text to fact-check
   - **File**: Upload images or videos for analysis
   - **Page**: Analyze the current webpage content
3. **Click "Fact Check"** and wait for results
4. **Use "Highlight Claims"** to mark verified content on the page

### Page Analysis

1. **Navigate to any webpage** with factual content
2. **Open the extension popup**
3. **Go to the "Page" tab**
4. **Click "Analyze Page"** to fact-check the main content
5. **Use "Highlight Claims"** to see results directly on the page

## 📊 Understanding Results

### Factuality Scores

- **🟢 80-100%**: Highly supported claims with strong evidence
- **🟡 50-79%**: Controversial claims with mixed evidence
- **🔴 0-49%**: Refuted claims with contradictory evidence
- **⚪ No Score**: Claims that couldn't be verified

### Evidence Types

- **SUPPORTS**: Evidence that confirms the claim
- **REFUTES**: Evidence that contradicts the claim
- **NEUTRAL**: Evidence that's related but doesn't confirm or deny

## 🔧 Troubleshooting

### Extension Not Working

1. **Check the backend server** is running on `localhost:2024`
2. **Verify API keys** are configured correctly in settings
3. **Test connection** using the button in settings
4. **Check Chrome's console** for error messages (F12 → Console)

### Common Issues

**"Backend service not available"**
- Ensure `python extension_backend.py` is running
- Check if port 2024 is available
- Try restarting the backend server

**"API key required"**
- Configure your Gemini API key in extension settings
- Verify the key is valid and has sufficient quota

**"No claims found"**
- Try shorter text snippets (under 5000 characters)
- Ensure the text contains factual claims, not just opinions
- Some content may not be suitable for fact-checking

### Performance Tips

1. **Limit text length** to under 2000 characters for faster processing
2. **Use specific claims** rather than general statements
3. **Check API quotas** if experiencing rate limits
4. **Close unused browser tabs** to free up memory

## 🔒 Privacy & Security

- **Local Processing**: All data is processed locally through your backend server
- **Secure Storage**: API keys are encrypted and stored securely
- **No Data Collection**: The extension doesn't collect or transmit personal data
- **Open Source**: All code is available for inspection and modification

## 🛠️ Development

### Project Structure

```
chrome-extension/
├── manifest.json          # Extension configuration
├── background.js          # Service worker for API communication
├── content.js             # Page interaction and text selection
├── content.css            # Styles for page overlays
├── popup.html             # Main extension interface
├── popup.js               # Popup functionality
├── popup.css              # Popup styles
├── options.html           # Settings page
├── options.js             # Settings functionality
├── options.css            # Settings styles
└── icons/                 # Extension icons
```

### Backend API Endpoints

- `GET /health` - Health check
- `POST /api/factcheck` - Fact-check text
- `POST /api/factcheck-file` - Fact-check uploaded files
- `GET /api/config` - Get configuration
- `POST /api/config` - Update configuration
- `GET /api/stats` - Get server statistics

### Building for Production

1. **Update version** in `manifest.json`
2. **Test thoroughly** on different websites
3. **Package the extension**:
   ```bash
   cd chrome-extension
   zip -r openfactverification-extension.zip .
   ```
4. **Submit to Chrome Web Store** (optional)

## 📚 Additional Resources

- **Original Project**: [OpenFactVerification on GitHub](https://github.com/Libr-AI/OpenFactVerification)
- **Gemini API Docs**: [Google AI Studio](https://makersuite.google.com/)
- **Serper API Docs**: [Serper.dev](https://serper.dev/playground)
- **Chrome Extension Docs**: [developer.chrome.com](https://developer.chrome.com/docs/extensions/)

## 🤝 Support

If you encounter issues:

1. **Check this README** for common solutions
2. **Review the backend logs** for error messages
3. **Test with the original web app** to isolate issues
4. **Open an issue** on the project repository

## 📄 License

This Chrome extension inherits the same license as the OpenFactVerification project. Please refer to the main project's LICENSE file for details.

---

**Happy Fact-Checking! 🔍✨**

*Keep the internet truthful, one claim at a time.*