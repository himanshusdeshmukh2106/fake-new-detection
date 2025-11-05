#!/usr/bin/env python3
"""Check available Gemini models and their limits"""

import google.generativeai as genai
import yaml

# Load API config
with open('api_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

genai.configure(api_key=config.get('GEMINI_API_KEY'))

print("Available Gemini Models:")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\nModel: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description[:100] if model.description else 'N/A'}...")
