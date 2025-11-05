#!/usr/bin/env python3
"""Quick script to test API keys"""

import google.generativeai as genai
import requests
import yaml

# Load API config
with open('api_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

GEMINI_API_KEY = config.get('GEMINI_API_KEY')
SERPER_API_KEY = config.get('SERPER_API_KEY')

print("=" * 60)
print("Testing API Keys")
print("=" * 60)

# Test Gemini API
print("\n1. Testing Gemini API Key...")
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Try different model names
    models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-pro']
    
    for model_name in models_to_try:
        try:
            print(f"   Trying model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("What is the name of the current US president?")
            print(f"✅ Gemini API Key is WORKING with model: {model_name}!")
            print(f"Response: {response.text[:200]}...")
            break
        except Exception as model_error:
            print(f"   ❌ Model {model_name} failed: {str(model_error)[:100]}")
            continue
except Exception as e:
    print(f"❌ Gemini API Key FAILED: {e}")

# Test Serper API
print("\n2. Testing Serper API Key...")
try:
    url = "https://google.serper.dev/search"
    payload = {"q": "current US president name"}
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("✅ Serper API Key is WORKING!")
        data = response.json()
        if 'organic' in data and len(data['organic']) > 0:
            print(f"Search result: {data['organic'][0].get('title', 'N/A')}")
    else:
        print(f"❌ Serper API Key FAILED: Status {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Serper API Key FAILED: {e}")

print("\n" + "=" * 60)
print("API Key Testing Complete")
print("=" * 60)
