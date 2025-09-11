# OpenFactVerification with Gemini API

This version of OpenFactVerification has been configured to work exclusively with Google's Gemini API.

## Quick Setup

1. **Get your Gemini API key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key for Gemini

2. **Configure API keys:**
   Edit the `api_config.yaml` file and add your keys:
   ```yaml
   SERPER_API_KEY: "your_serper_api_key_here"  # For web search
   GEMINI_API_KEY: "your_gemini_api_key_here"  # For LLM operations
   ```

3. **Install dependencies (already done):**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Web Interface
```bash
python webapp.py --api_config api_config.yaml
```
Then open your browser to `http://localhost:2024`

### Command Line (Text)
```bash
python -m factcheck --modal text --input demo_data/text.txt --api_config api_config.yaml
```

### Command Line (String)
```bash
python -m factcheck --modal string --input "Your text to fact-check here" --api_config api_config.yaml
```

## Available Models

The system now supports these Gemini models:
- `gemini-1.5-pro` (default)
- `gemini-1.5-flash`
- `gemini-pro`

Example with specific model:
```bash
python webapp.py --model gemini-1.5-flash --api_config api_config.yaml
```

## Notes

- **SERPER_API_KEY**: Required for web search evidence retrieval
- **GEMINI_API_KEY**: Required for all AI text processing (decomposition, verification, etc.)
- The system has been optimized for Gemini's rate limits (15 requests/minute)
- All other LLM providers (OpenAI, Claude, local models) have been removed