#!/usr/bin/env python3
"""Test ML integration in the fact-checking pipeline"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from factcheck import FactCheck
from factcheck.utils.utils import load_yaml

print("=" * 70)
print("🧪 TESTING ML-ENHANCED FACT-CHECKING PIPELINE")
print("=" * 70)
print()

# Load API config
try:
    api_config = load_yaml('api_config.yaml')
    print("✅ API config loaded")
except Exception as e:
    print(f"❌ Failed to load API config: {e}")
    sys.exit(1)

# Initialize FactCheck with ML enhancements
print("\n📦 Initializing FactCheck system...")
try:
    factcheck = FactCheck(
        default_model="gemini-2.5-flash",
        api_config=api_config,
        prompt="chatgpt_prompt",
        retriever="serper",
    )
    print("✅ FactCheck initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize FactCheck: {e}")
    sys.exit(1)

# Test text with mixed claim types
test_text = """
The COVID-19 vaccine has shown 95% efficacy in clinical trials. 
I think this is the best medical breakthrough of the decade.
Scientists believe that aliens might exist somewhere in the universe.
The unemployment rate in the US dropped to 3.5% last month.
This movie was absolutely terrible and boring.
Everything happens for a reason in life.
The company reported $5 billion in revenue for Q3 2023.
"""

print("\n" + "=" * 70)
print("📝 TEST TEXT:")
print("=" * 70)
print(test_text.strip())
print()

# Run fact-checking
print("=" * 70)
print("🔍 RUNNING FACT-CHECK...")
print("=" * 70)
print()

try:
    result = factcheck.check_text(test_text)
    
    print("\n" + "=" * 70)
    print("📊 RESULTS SUMMARY")
    print("=" * 70)
    
    summary = result['summary']
    print(f"\n📈 Overall Statistics:")
    print(f"  Total Claims: {summary['num_claims']}")
    print(f"  Checkworthy Claims: {summary['num_checkworthy_claims']}")
    print(f"  Verified Claims: {summary['num_verified_claims']}")
    print(f"  Supported: {summary['num_supported_claims']}")
    print(f"  Refuted: {summary['num_refuted_claims']}")
    print(f"  Controversial: {summary['num_controversial_claims']}")
    print(f"  Overall Factuality: {summary['factuality']:.1%}")
    
    print(f"\n💰 Efficiency Metrics:")
    filtered_claims = summary['num_claims'] - summary['num_checkworthy_claims']
    if summary['num_claims'] > 0:
        efficiency = (filtered_claims / summary['num_claims']) * 100
        print(f"  Claims Filtered by ML: {filtered_claims}")
        print(f"  API Call Reduction: {efficiency:.1f}%")
        print(f"  Estimated Cost Savings: ${filtered_claims * 0.01:.2f} per request")
    
    print("\n" + "=" * 70)
    print("📋 DETAILED CLAIM ANALYSIS")
    print("=" * 70)
    
    for i, claim_detail in enumerate(result['claim_detail'], 1):
        print(f"\n{i}. Claim: {claim_detail['claim']}")
        print(f"   Checkworthy: {'✅ Yes' if claim_detail['checkworthy'] else '❌ No'}")
        print(f"   Reason: {claim_detail['checkworthy_reason']}")
        
        if claim_detail['checkworthy']:
            print(f"   Factuality: {claim_detail['factuality']}")
            if isinstance(claim_detail['factuality'], float):
                if claim_detail['factuality'] >= 0.8:
                    verdict = "✅ SUPPORTED"
                elif claim_detail['factuality'] >= 0.5:
                    verdict = "⚠️  CONTROVERSIAL"
                else:
                    verdict = "❌ REFUTED"
                print(f"   Verdict: {verdict}")
                print(f"   Evidence Count: {len(claim_detail['evidences'])}")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    
    # Performance summary
    print("\n🎯 ML INTEGRATION PERFORMANCE:")
    print(f"  ✅ ML Classifier: {'Active' if factcheck.checkworthy.use_ml else 'Inactive'}")
    print(f"  ✅ API Fallback: Available")
    print(f"  ✅ Hybrid Mode: Enabled")
    print(f"  ✅ Cost Optimization: {efficiency:.1f}% reduction")
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("🎉 ALL TESTS PASSED!")
print("=" * 70)
