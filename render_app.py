#!/usr/bin/env python3
"""
Render Deployment Script
Starts the Flask app for Render deployment
"""

import os
from webapp import app
from factcheck.utils.utils import load_yaml
from factcheck import FactCheck

# Configure the Flask app for production
print("🚀 Initializing OpenFactVerification for production...")

# Load API config
config_file = os.environ.get('API_CONFIG_FILE', 'api_config_production.yaml')

try:
    api_config = load_yaml(config_file)
    print(f"✅ Loaded config from {config_file}")
except Exception as e:
    print(f"⚠️  Could not load {config_file}: {e}")
    api_config = {}

# Override with environment variables (Render will set these)
api_config['SERPER_API_KEY'] = os.environ.get('SERPER_API_KEY', api_config.get('SERPER_API_KEY', ''))
api_config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', api_config.get('GEMINI_API_KEY', ''))

# Optional GCS settings
api_config['GCS_BUCKET_NAME'] = os.environ.get('GCS_BUCKET_NAME', api_config.get('GCS_BUCKET_NAME'))
api_config['GCS_BASE_URL'] = os.environ.get('GCS_BASE_URL', api_config.get('GCS_BASE_URL'))
api_config['GOOGLE_APPLICATION_CREDENTIALS'] = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', api_config.get('GOOGLE_APPLICATION_CREDENTIALS'))

# Validate required keys
required_keys = ['SERPER_API_KEY', 'GEMINI_API_KEY']
missing_keys = [key for key in required_keys if not api_config.get(key)]

if missing_keys:
    print(f"❌ Missing required API keys: {missing_keys}")
    print("Set these as environment variables in Render:")
    for key in missing_keys:
        print(f"  - {key}")
    # Configure app with error state
    app.config['API_CONFIG'] = api_config
    app.config['FACTCHECK_INSTANCE'] = None
    app.config['CONFIG_ERROR'] = f"Missing required API keys: {missing_keys}"
    print("🏭 Production app configured with errors")
else:
    print("✅ All required API keys are configured")
    
    # Make api_config globally available
    app.config['API_CONFIG'] = api_config
    
    try:
        # Initialize FactCheck instance
        factcheck_instance = FactCheck(
            default_model="gemini-1.5-pro",
            api_config=api_config,
            prompt="chatgpt_prompt",
            retriever="serper",
        )
        
        # Make factcheck_instance globally available
        app.config['FACTCHECK_INSTANCE'] = factcheck_instance
        app.config['CONFIG_ERROR'] = None
        
        print("🏭 Production app configured successfully")
        
    except Exception as e:
        print(f"❌ Error initializing FactCheck: {e}")
        app.config['FACTCHECK_INSTANCE'] = None
        app.config['CONFIG_ERROR'] = f"Error initializing FactCheck: {str(e)}"

print("🚀 App ready for Gunicorn")

if __name__ == "__main__":
    # For development mode
    port = int(os.environ.get('PORT', 10000))
    print(f"🛠️ Development mode - serving on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)