#!/usr/bin/env python3
"""
Test script to verify the JSON parsing fixes for Gemini responses.
"""

import json
import re

def clean_gemini_response(response):
    """
    Clean malformed JSON responses from Gemini
    """
    cleaned_response = response.strip()
    
    # Try to fix common JSON formatting issues
    if cleaned_response.startswith('{') and not cleaned_response.endswith('}'):
        # Missing closing brace
        cleaned_response += '}'
    elif cleaned_response.startswith('{{') and not cleaned_response.endswith('}}'):
        # Double braces from Gemini, fix it
        cleaned_response = cleaned_response[1:-1] if cleaned_response.endswith('}') else cleaned_response[1:] + '}'
    
    # Remove any markdown code blocks
    cleaned_response = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', cleaned_response)
    cleaned_response = cleaned_response.strip()
    
    return cleaned_response

def test_json_parsing():
    """Test various malformed JSON responses that Gemini might return"""
    
    # Test case 1: Missing closing brace (actual error from logs)
    malformed_json1 = '''{\n"Brain's blood vessels could stretch 100,000 miles if lined up.": "If you were to put all of the blood vessels that are in the brain in a single line, it would stretch 100,000 miles."'''
    
    print("Test 1: Missing closing brace")
    print("Original:", repr(malformed_json1))
    
    try:
        cleaned = clean_gemini_response(malformed_json1)
        parsed = json.loads(cleaned)
        print("✅ Successfully parsed:", parsed)
    except Exception as e:
        print("❌ Failed to parse:", e)
    
    print("\n" + "-"*50 + "\n")
    
    # Test case 2: Claims decomposition format
    malformed_json2 = '''{\n"claims": ["Brain's blood vessels could stretch 100,000 miles if lined up."]'''
    
    print("Test 2: Claims decomposition format")
    print("Original:", repr(malformed_json2))
    
    try:
        cleaned = clean_gemini_response(malformed_json2)
        parsed = json.loads(cleaned)
        print("✅ Successfully parsed:", parsed)
        print("Claims:", parsed.get("claims", []))
    except Exception as e:
        print("❌ Failed to parse:", e)
    
    print("\n" + "-"*50 + "\n")
    
    # Test case 3: With markdown code blocks
    malformed_json3 = '''```json\n{\n"claims": ["Brain's blood vessels could stretch 100,000 miles if lined up."]\n}\n```'''
    
    print("Test 3: With markdown code blocks")
    print("Original:", repr(malformed_json3))
    
    try:
        cleaned = clean_gemini_response(malformed_json3)
        parsed = json.loads(cleaned)
        print("✅ Successfully parsed:", parsed)
    except Exception as e:
        print("❌ Failed to parse:", e)

if __name__ == "__main__":
    test_json_parsing()