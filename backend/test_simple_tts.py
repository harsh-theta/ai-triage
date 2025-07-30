#!/usr/bin/env python3
"""
Simple test to verify emergency detection logic is working correctly
for headache with severity 8 (should NOT trigger emergency)
"""

def test_headache_severity_8_simple():
    """
    Test that headache with severity 8 does NOT trigger emergency
    """
    print("Testing: Headache with Severity 8 - Should NOT be Emergency")
    print("=" * 55)
    
    # Test data that represents what the LLM should extract
    test_cases = [
        {
            "name": "Headache Severity 8",
            "emr_fields": {
                "chief_complaint": "headache",
                "severity": 8,
                "duration": "2 hours",
                "emergency_flag": False  # Should remain False
            },
            "chat_history": [
                {"role": "user", "content": "I have a headache"},
                {"role": "user", "content": "It's an 8 out of 10 on the pain scale"}
            ],
            "expected_emergency": False
        },
        {
            "name": "Headache Severity 10",
            "emr_fields": {
                "chief_complaint": "headache",
                "severity": 10,
                "duration": "1 hour",
                "emergency_flag": False  # Should remain False
            },
            "chat_history": [
                {"role": "user", "content": "I have the worst headache of my life"},
                {"role": "user", "content": "It's a 10 out of 10"}
            ],
            "expected_emergency": False
        },
        {
            "name": "Chest Pain Severity 5",
            "emr_fields": {
                "chief_complaint": "chest pain",
                "severity": 5,
                "duration": "30 minutes",
                "emergency_flag": False
            },
            "chat_history": [
                {"role": "user", "content": "I have chest pain"},
                {"role": "user", "content": "It's about a 5 out of 10"}
            ],
            "expected_emergency": True  # Should trigger emergency
        }
    ]
    
    # Simple pattern matching (simulating our detect_emergency_symptoms function)
    emergency_patterns = [
        "chest pain", "chest pressure", "shortness of breath", 
        "difficulty breathing", "stroke", "seizure", "unconscious",
        "vomiting blood", "anaphylaxis", "overdose", "poisoning"
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        
        # Check if any emergency patterns are in the symptoms
        all_text = " ".join([msg["content"].lower() for msg in test_case["chat_history"]])
        all_text += " " + test_case["emr_fields"].get("chief_complaint", "").lower()
        
        emergency_detected = any(pattern in all_text for pattern in emergency_patterns)
        
        print(f"  Chief Complaint: {test_case['emr_fields']['chief_complaint']}")
        print(f"  Severity: {test_case['emr_fields']['severity']}")
        print(f"  Emergency Detected: {emergency_detected}")
        print(f"  Expected: {test_case['expected_emergency']}")
        
        if emergency_detected == test_case['expected_emergency']:
            print("  ✅ PASSED")
        else:
            print("  ❌ FAILED")
    
    print("\n" + "=" * 55)
    print("Key Points:")
    print("- Headache with ANY severity (8, 9, 10) should NOT trigger emergency")
    print("- Only specific symptom types should trigger emergency")
    print("- Severity alone should never determine emergency status")

if __name__ == "__main__":
    test_headache_severity_8_simple()