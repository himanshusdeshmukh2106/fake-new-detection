# OpenFactVerification

An open-source tool for automated fact verification that provides a comprehensive pipeline for analyzing texts, extracting claims, searching for evidence, and verifying claims.

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/himanshusdeshmukh2106/fake-new-detection.git
cd fake-new-detection
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Download spaCy language model:**
```bash
python -m spacy download en_core_web_sm
```

## Configuration

1. **Rename the configuration file:**
```bash
cp api_config_production.yaml api_config.yaml
```

2. **Add your API keys** to `api_config.yaml`:
```yaml
SERPER_API_KEY: "your_serper_api_key_here"
GEMINI_API_KEY: "your_gemini_api_key_here"
```

## Usage

### Web Application

1. **Start the main web application:**
```bash
python webapp.py --config api_config.yaml
```

2. **Start the Chrome extension backend** (in a separate terminal):
```bash
python extension_backend.py
```

### Chrome Extension

1. **Load the extension in Chrome:**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `chrome-extension` folder
   - Pin the extension to your toolbar

2. **Use the extension:**
   - Make sure the extension backend is running (`python extension_backend.py`)
   - Click the extension icon in your browser toolbar
   - Use the fact-checking features directly in your browser

## API Keys Required

- **SERPER_API_KEY**: Get from [Serper.dev](https://serper.dev) for web search functionality
- **GEMINI_API_KEY**: Get from [Google AI Studio](https://aistudio.google.com) for AI processing

## Features

- Text analysis and claim extraction
- Evidence retrieval from web sources
- Automated claim verification
- Chrome extension for browser integration
- Multimodal input support (text, images, videos)

## Contributing

Welcome contributions! Please feel free to submit issues and pull requests.

## License

This project is open source. Please check the license file for more details.