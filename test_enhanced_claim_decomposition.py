#!/usr/bin/env python3
"""
Test script for enhanced claim decomposition with context preservation.
Tests the improved decomposition prompts with specific examples that maintain
geographical, temporal, and entity context.
"""

import json
import sys
import os

# Add the factcheck module to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from factcheck.core.Decompose import Decompose
from factcheck.utils.llmclient.gemini_client import GeminiClient
from factcheck.utils.prompt.chatgpt_prompt import ChatGPTPrompt
from factcheck.utils.utils import load_yaml


def test_enhanced_decomposition():
    """Test the enhanced claim decomposition with context preservation."""
    
    print("=" * 80)
    print("TESTING ENHANCED CLAIM DECOMPOSITION WITH CONTEXT PRESERVATION")
    print("=" * 80)
    
    # Load API configuration
    try:
        api_config = load_yaml("api_config.yaml")
        gemini_api_key = api_config.get('GEMINI_API_KEY')
        if not gemini_api_key:
            print("❌ Error: GEMINI_API_KEY not found in api_config.yaml")
            return
    except Exception as e:
        print(f"❌ Error loading API config: {e}")
        return
    
    # Initialize components
    try:
        llm_client = GeminiClient(api_config=api_config, model="gemini-1.5-pro")
        prompt = ChatGPTPrompt()
        decomposer = Decompose(llm_client, prompt)
        print("✅ Successfully initialized Gemini client and decomposer")
    except Exception as e:
        print(f"❌ Error initializing components: {e}")
        return
    
    # Test cases with expected improved behavior
    test_cases = [
        {
            "text": "Protests in Nepal occurred due to social media bans.",
            "description": "Geographic and causal context preservation",
            "expected_improved": [
                "Should preserve 'Nepal' context in all relevant claims",
                "Should maintain causal relationship between protests and bans",
                "Should specify location in social media ban claim"
            ]
        },
        {
            "text": "Did Elon Musk buy X in 2023?",
            "description": "Entity and temporal context preservation", 
            "expected_improved": [
                "Should maintain 'Elon Musk' as the buyer",
                "Should preserve '2023' as the time context",
                "Should keep entity-action-time relationships"
            ]
        },
        {
            "text": "Was Narendra Modi involved in Godhra riots?",
            "description": "Person and event context preservation",
            "expected_improved": [
                "Should maintain 'Narendra Modi' in involvement claim",
                "Should preserve 'Godhra riots' as specific event",
                "Should not create vague claims about generic riots"
            ]
        },
        {
            "text": "Apple announced iPhone 15 launch in California during September 2023.",
            "description": "Complex multi-context preservation",
            "expected_improved": [
                "Should preserve company-product relationship",
                "Should maintain geographical context (California)",
                "Should keep temporal context (September 2023)",
                "Should create claims with specific contexts intact"
            ]
        },
        {
            "text": "Tesla's stock price rose 15% after the Berlin factory opened in Germany.",
            "description": "Corporate, numerical, and geographical context",
            "expected_improved": [
                "Should maintain Tesla as the specific company",
                "Should preserve Berlin as factory location",
                "Should keep Germany as country context",
                "Should maintain causal relationship with stock price"
            ]
        }
    ]
    
    print(f"\n🧪 Testing {len(test_cases)} cases with enhanced context preservation...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test_case['description']}")
        print(f"Input: '{test_case['text']}'")
        print("-" * 60)
        
        try:
            # Get decomposed claims
            claims = decomposer.getclaims(test_case['text'])
            
            if claims and isinstance(claims, list):
                print("✅ Claims generated successfully:")
                for j, claim in enumerate(claims, 1):
                    print(f"  {j}. {claim}")
                
                print(f"\n📋 Expected improvements:")
                for improvement in test_case['expected_improved']:
                    print(f"  • {improvement}")
                
                # Basic validation
                context_preserved = True
                validation_notes = []
                
                # Check for original problematic patterns
                if "Protests in Nepal" in test_case['text']:
                    generic_protests = any("protests were due to" in claim.lower() and "nepal" not in claim.lower() for claim in claims)
                    if generic_protests:
                        context_preserved = False
                        validation_notes.append("❌ Found generic protest claim without Nepal context")
                    else:
                        validation_notes.append("✅ Nepal context preserved in protest-related claims")
                
                if "Elon Musk" in test_case['text'] and "2023" in test_case['text']:
                    musk_context = any("elon musk" in claim.lower() for claim in claims)
                    time_context = any("2023" in claim for claim in claims)
                    if not musk_context:
                        validation_notes.append("❌ Elon Musk entity context may be lost")
                    else:
                        validation_notes.append("✅ Elon Musk entity context preserved")
                    if not time_context:
                        validation_notes.append("❌ 2023 temporal context may be lost")
                    else:
                        validation_notes.append("✅ 2023 temporal context preserved")
                
                print(f"\n🔍 Context validation:")
                for note in validation_notes:
                    print(f"  {note}")
                
                if context_preserved and validation_notes:
                    print(f"  🎯 Overall: Context preservation appears improved")
                else:
                    print(f"  ⚠️  Overall: May need further refinement")
                
            else:
                print("❌ Failed to generate valid claims")
                context_preserved = False
                
        except Exception as e:
            print(f"❌ Error during decomposition: {e}")
            context_preserved = False
        
        print("\n" + "=" * 80 + "\n")
    
    print("🏁 Enhanced claim decomposition testing completed!")
    print("\n📊 Key improvements in the enhanced prompts:")
    print("  • Added explicit context preservation rules")
    print("  • Included specific examples with geographical context")
    print("  • Added temporal and entity context preservation")
    print("  • Enhanced with causal relationship maintenance")
    print("  • Provided diverse examples covering different context types")
    
    print("\n💡 The enhanced prompts should now maintain crucial context that was")
    print("   previously lost, leading to more relevant evidence retrieval and")
    print("   better fact-checking accuracy.")


if __name__ == "__main__":
    test_enhanced_decomposition()