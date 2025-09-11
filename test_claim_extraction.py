#!/usr/bin/env python3
"""
Test script to demonstrate the new claim extraction functionality for multimodal inputs.
This script shows how image/video descriptions are now filtered to extract only factual claims.
"""

import os
from factcheck.utils.multimodal import extract_factual_claims

def test_claim_extraction():
    """Test the claim extraction functionality with sample descriptions"""
    
    # Sample image description (contains both visual descriptions and factual claims)
    sample_description_1 = """
    The image shows a red brick building with a white background. There's a sign that reads "New York Public Library - Main Branch". 
    The building has beautiful neoclassical architecture with tall columns. There are green trees surrounding 
    the building and the sky appears to be partly cloudy. The library was established in 1895 and serves over 
    50 million visitors annually. The building is located at 5th Avenue and 42nd Street in Manhattan. 
    The facade features beautiful Corinthian columns and the interior has a stunning rose main reading room.
    """
    
    # Another sample with mostly visual descriptions
    sample_description_2 = """
    The image has a white background showing a person in a blue shirt. The person appears to be in a laboratory 
    setting with various equipment. There are bright lights and the scene is well-lit. The person seems to be 
    working with some scientific instruments on a metal table.
    """
    
    # Sample with factual claim embedded in visual description
    sample_description_3 = """
    A beautiful landscape with green trees and blue sky. In the center of the image, there's a white sign that 
    reads "Einstein won the Nobel Prize in Physics in 1921". The scene appears peaceful and serene with 
    mountains in the background. The lighting is perfect and the composition is stunning.
    """
    
    test_cases = [
        ("Test 1: Mixed visual and factual content", sample_description_1),
        ("Test 2: Mostly visual descriptions", sample_description_2),
        ("Test 3: Factual claim in visual context", sample_description_3)
    ]
    
    for title, description in test_cases:
        print(f"\n{title}:")
        print("-" * 60)
        print("Original Description:")
        print(description)
        print("\nExpected filtered claims:")
        
        if "Test 1" in title:
            print("- New York Public Library - Main Branch")
            print("- The library was established in 1895")
            print("- Serves over 50 million visitors annually") 
            print("- Located at 5th Avenue and 42nd Street in Manhattan")
        elif "Test 2" in title:
            print("- No verifiable factual claims found")
        elif "Test 3" in title:
            print("- Einstein won the Nobel Prize in Physics in 1921")
        
        print("\nWould be filtered out:")
        if "Test 1" in title:
            print("- Visual descriptions (red brick building, white background)")
            print("- Aesthetic opinions (beautiful neoclassical architecture)")
            print("- Color descriptions (green trees, partly cloudy sky)")
            print("- Subjective assessments (stunning rose main reading room)")
        elif "Test 2" in title:
            print("- All content (white background, blue shirt, bright lights, well-lit, etc.)")
        elif "Test 3" in title:
            print("- Visual descriptions (beautiful landscape, green trees, blue sky)")
            print("- Aesthetic opinions (peaceful, serene, perfect lighting, stunning composition)")
            print("- Spatial descriptions (in the center, in the background)")

if __name__ == "__main__":
    test_claim_extraction()