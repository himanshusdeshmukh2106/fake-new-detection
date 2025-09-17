#!/usr/bin/env python3
"""
OpenFactVerification Chrome Extension Backend Server
A lightweight Flask server that acts as a proxy between the Chrome extension and the FactCheck module.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from factcheck.utils.llmclient import CLIENTS
from factcheck.utils.multimodal import modal_normalization
from factcheck.utils.utils import load_yaml
from factcheck import FactCheck
import argparse
import json
import os
import tempfile
import threading
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Global variables for the fact check instance
factcheck_instance = None
api_config = {}
extension_config = {
    'max_claims': 10,
    'timeout_seconds': 120,
    'enable_debug': False
}

def initialize_factcheck(config_path="api_config.yaml"):
    """Initialize the FactCheck instance with configuration."""
    global factcheck_instance, api_config
    
    try:
        # Load API config
        if os.path.exists(config_path):
            api_config = load_yaml(config_path)
            logger.info(f"Loaded API config from {config_path}")
        else:
            logger.warning(f"Config file {config_path} not found, using environment variables")
            api_config = {
                'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
                'SERPER_API_KEY': os.getenv('SERPER_API_KEY')
            }

        # Initialize FactCheck instance
        factcheck_instance = FactCheck(
            default_model="gemini-1.5-pro",
            api_config=api_config,
            prompt="chatgpt_prompt",
            retriever="serper",
        )
        
        logger.info("FactCheck instance initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize FactCheck: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the Chrome extension."""
    status = {
        'status': 'healthy',
        'factcheck_ready': factcheck_instance is not None,
        'timestamp': time.time()
    }
    return jsonify(status)

@app.route('/api/factcheck', methods=['POST'])
def factcheck_text():
    """Fact-check text content."""
    if not factcheck_instance:
        return jsonify({
            'success': False,
            'error': 'FactCheck service not initialized. Please check server configuration.'
        }), 503

    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'No text provided for fact-checking'
            }), 400

        text = data['text'].strip()
        if not text:
            return jsonify({
                'success': False,
                'error': 'Empty text provided'
            }), 400

        # Limit text length to prevent API overload
        max_length = 5000
        if len(text) > max_length:
            text = text[:max_length]
            logger.info(f"Text truncated to {max_length} characters")

        logger.info(f"Processing fact-check request for text of length {len(text)}")
        
        # Process with timeout
        result = factcheck_instance.check_text(text)
        
        # Limit the number of claims if configured
        if result and 'claim_detail' in result:
            max_claims = extension_config.get('max_claims', 10)
            if len(result['claim_detail']) > max_claims:
                result['claim_detail'] = result['claim_detail'][:max_claims]
                logger.info(f"Limited results to {max_claims} claims")

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"Error in fact-checking: {e}")
        return jsonify({
            'success': False,
            'error': f'Fact-checking failed: {str(e)}'
        }), 500

@app.route('/api/factcheck-file', methods=['POST'])
def factcheck_file():
    """Fact-check uploaded file (image or video)."""
    if not factcheck_instance:
        return jsonify({
            'success': False,
            'error': 'FactCheck service not initialized. Please check server configuration.'
        }), 503

    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400

        file = request.files['file']
        file_type = request.form.get('type', 'image')

        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Validate file type
        allowed_extensions = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v']
        }
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions.get(file_type, []):
            return jsonify({
                'success': False,
                'error': f'Unsupported file type: {file_ext}'
            }), 400

        # Save file temporarily
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        
        # Validate saved file
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'Failed to save uploaded file'
            }), 500
            
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return jsonify({
                'success': False,
                'error': 'Uploaded file is empty'
            }), 400
            
        logger.info(f"File saved successfully: {file_path} (size: {file_size} bytes)")
        
        # Debug: Check file content
        try:
            with open(file_path, 'rb') as debug_file:
                first_bytes = debug_file.read(16)
                logger.info(f"First 16 bytes of file: {first_bytes}")
        except Exception as debug_error:
            logger.warning(f"Could not read file for debugging: {debug_error}")

        try:
            logger.info(f"Processing {file_type} file: {file.filename}")
            
            # Additional validation for image files
            if file_type == 'image':
                try:
                    from PIL import Image
                    with Image.open(file_path) as img:
                        logger.info(f"Image validation successful: {img.format} {img.size} {img.mode}")
                except Exception as img_error:
                    logger.error(f"Image validation failed: {img_error}")
                    return jsonify({
                        'success': False,
                        'error': f'Invalid image file: {str(img_error)}'
                    }), 400
            
            # Process the file using multimodal processing
            text_content = modal_normalization(
                modal=file_type,
                input=file_path,
                gemini_api_key=api_config.get('GEMINI_API_KEY'),
                api_config=api_config
            )

            if not text_content or text_content.strip() == "":
                logger.warning("No text content extracted from file")
                text_content = "No extractable content found in the file"

            # Process with fact-checking
            result = factcheck_instance.check_text(text_content)
            
            # Limit the number of claims if configured
            if result and 'claim_detail' in result:
                max_claims = extension_config.get('max_claims', 10)
                if len(result['claim_detail']) > max_claims:
                    result['claim_detail'] = result['claim_detail'][:max_claims]

            return jsonify({
                'success': True,
                'data': result,
                'extracted_text': text_content[:500] + ('...' if len(text_content) > 500 else '')
            })

        finally:
            # Clean up temporary file
            try:
                os.remove(file_path)
                os.rmdir(temp_dir)
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary files: {cleanup_error}")

    except Exception as e:
        logger.error(f"Error in file fact-checking: {e}")
        return jsonify({
            'success': False,
            'error': f'File processing failed: {str(e)}'
        }), 500

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Handle configuration updates from the extension."""
    global extension_config, api_config, factcheck_instance
    
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'config': {
                **extension_config,
                'api_keys_configured': bool(api_config.get('GEMINI_API_KEY'))
            }
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No configuration data provided'
                }), 400

            # Update extension config
            if 'max_claims' in data:
                extension_config['max_claims'] = max(1, min(50, int(data['max_claims'])))
            if 'timeout_seconds' in data:
                extension_config['timeout_seconds'] = max(30, min(300, int(data['timeout_seconds'])))
            if 'enable_debug' in data:
                extension_config['enable_debug'] = bool(data['enable_debug'])

            # Update API config if keys provided
            if 'gemini_api_key' in data and data['gemini_api_key'].strip():
                api_config['GEMINI_API_KEY'] = data['gemini_api_key'].strip()
            if 'serper_api_key' in data and data['serper_api_key'].strip():
                api_config['SERPER_API_KEY'] = data['serper_api_key'].strip()

            # Reinitialize FactCheck if API keys changed
            if 'gemini_api_key' in data or 'serper_api_key' in data:
                logger.info("Reinitializing FactCheck with new API keys")
                factcheck_instance = FactCheck(
                    default_model="gemini-1.5-pro",
                    api_config=api_config,
                    prompt="chatgpt_prompt",
                    retriever="serper",
                )

            return jsonify({
                'success': True,
                'message': 'Configuration updated successfully'
            })

        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return jsonify({
                'success': False,
                'error': f'Configuration update failed: {str(e)}'
            }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get server statistics."""
    stats = {
        'server_uptime': time.time() - app._start_time if hasattr(app, '_start_time') else 0,
        'factcheck_ready': factcheck_instance is not None,
        'config': extension_config,
        'api_keys_configured': {
            'gemini': bool(api_config.get('GEMINI_API_KEY')),
            'serper': bool(api_config.get('SERPER_API_KEY'))
        }
    }
    return jsonify(stats)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

def run_server(host='localhost', port=2024, debug=False):
    """Run the Flask server."""
    logger.info(f"Starting OpenFactVerification Extension Backend on {host}:{port}")
    logger.info("Make sure to configure your API keys before using the extension")
    
    app._start_time = time.time()
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenFactVerification Chrome Extension Backend')
    parser.add_argument('--host', type=str, default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=2024, help='Port to bind to (default: 2024)')
    parser.add_argument('--config', type=str, default='api_config.yaml', help='Path to API config file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    # Initialize the FactCheck instance
    if not initialize_factcheck(args.config):
        logger.error("Failed to initialize FactCheck. Please check your configuration.")
        logger.info("You can still start the server and configure API keys through the extension settings.")

    # Start the server
    try:
        run_server(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")