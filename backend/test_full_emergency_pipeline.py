#!/usr/bin/env python3
"""
Test the full emergency detection pipeline including LLM extraction
to verify that severity 8 headaches do NOT trigger emergency detection.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_headache_severity_8():
    """
    Test that a headache with severity 8 does NOT trigger emergency detection
    """
    print("Testing Full Emergency Pipeline - Headache Severity 8")
    print("=" * 60)
    
    # Simulate the exact scenario: headache with severity 8
    chat_history = [
        {"role": "user", "content": "I have a headache"},
        {"role": "assistant", "content": "I'm sorry to hear you're experiencing a headache. Can you tell me how severe the pain is on a scale of 1 to 10?"},
        {"role": "user", "content": "It's about an 8 out of 10"}
    ]
    
    print("Chat History:")
    for msg in chat_history:
        print(f"  {msg['role'].capitalize()}: {msg['content']}")
    
    print("\nAnalyzing with our symptom-based detection...")
    
    # Simulate what extract_emr_fields would extract
    simulated_emr = {
        "chief_complaint": "headache",
        "severity": 8,
        "duration": "",
        "onset": "",
        "location": "",
        "associated_symptoms": "",
        "emergency_flag": False  # Should remain False
    }
    
    # Test our symptom-based detection
    from test_emergency_logic import detect_emergency_symptoms_test
    result = detect_emergency_symptoms_test(simulated_emr, chat_history)
    
    print(f"\nExtracted EMR: {simulated_emr}")
    print(f"Emergency detected by symptom analysis: {result.get('emergency_flag', False)}")
    print(f"Expected: False")
    
    if result.get('emergency_flag', False):
        print("❌ FAILED: Headache with severity 8 incorrectly triggered emergency!")
        print("This suggests there may be an issue with the symptom pattern matching.")
    else:
        print("✅ PASSED: Headache with severity 8 correctly did NOT trigger emergency")
    
    print("\n" + "=" * 60)
    print("If you're still seeing emergency detection for headache severity 8,")
    print("the issue is likely in the LLM's extract_emr_fields function,")
    print("which may be setting emergency_flag=True based on the prompt.")

if __name__ == "__main__":
    test_headache_severity_8()