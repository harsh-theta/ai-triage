#!/usr/bin/env python3
"""
Test script to verify emergency detection logic works based on symptoms only,
not on severity or duration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simple test function without importing the full agent_graph
def detect_emergency_symptoms_test(emr_fields: dict, chat_history: list) -> dict:
    """
    Simplified version of detect_emergency_symptoms for testing
    """
    # Get all user messages to analyze symptoms
    user_messages = [msg["content"].lower() for msg in chat_history if msg["role"] == "user"]
    all_user_text = " ".join(user_messages)
    
    # Get chief complaint and associated symptoms
    chief_complaint = (emr_fields.get("chief_complaint") or "")
    if isinstance(chief_complaint, str):
        chief_complaint = chief_complaint.lower()
    else:
        chief_complaint = ""
    
    # Handle associated_symptoms which can be string or list
    associated_symptoms = emr_fields.get("associated_symptoms") or ""
    if isinstance(associated_symptoms, list):
        associated_symptoms = " ".join(str(item) for item in associated_symptoms if item).lower()
    elif isinstance(associated_symptoms, str):
        associated_symptoms = associated_symptoms.lower()
    else:
        associated_symptoms = ""
    
    # Combine all symptom text for analysis
    symptom_text = f"{all_user_text} {chief_complaint} {associated_symptoms}".lower()
    
    # Define emergency symptom patterns - based on symptom nature, not severity
    emergency_patterns = [
        # Cardiac emergencies
        "chest pain", "chest pressure", "chest tightness", "heart attack", "cardiac arrest",
        "crushing chest pain", "radiating pain", "left arm pain",
        
        # Respiratory emergencies  
        "shortness of breath", "difficulty breathing", "can't breathe", "cannot breathe",
        "trouble breathing", "gasping", "choking", "respiratory distress",
        
        # Neurological emergencies
        "stroke", "loss of consciousness", "unconscious", "seizure", "paralysis", 
        "weakness on one side", "slurred speech", "vision loss", "sudden vision",
        
        # Bleeding/trauma
        "uncontrolled bleeding", "major trauma", "head injury", "compound fracture",
        
        # Abdominal emergencies
        "appendicitis", "vomiting blood", "blood in vomit",
        
        # Allergic reactions
        "anaphylaxis", "throat closing", "difficulty swallowing",
        
        # Other critical emergencies
        "overdose", "poisoning", "suicide", "self harm",
        "emergency", "911", "hospital", "ambulance"
    ]
    
    # Check for emergency patterns
    emergency_detected = False
    detected_symptoms = []
    
    for pattern in emergency_patterns:
        if pattern in symptom_text:
            emergency_detected = True
            detected_symptoms.append(pattern)
    
    # Update EMR fields if emergency detected
    if emergency_detected:
        emr_fields["emergency_flag"] = True
        print(f"Emergency detected! Symptoms: {detected_symptoms}")
    
    return emr_fields

def test_emergency_detection():
    print("Testing Emergency Detection Logic - Symptoms Only")
    print("=" * 50)
    
    # Test Case 1: Emergency symptom (chest pain) should trigger emergency
    print("\nTest 1: Emergency symptom (chest pain)")
    emr_fields = {
        "chief_complaint": "chest pain",
        "severity": 5,  # Low severity but emergency symptom
        "duration": "1 hour"
    }
    chat_history = [
        {"role": "user", "content": "I have chest pain"}
    ]
    result = detect_emergency_symptoms_test(emr_fields, chat_history)
    print(f"EMR: {emr_fields}")
    print(f"Emergency detected: {result.get('emergency_flag', False)}")
    print(f"Expected: True (chest pain is emergency symptom)")
    
    # Test Case 2: High severity but non-emergency symptom should NOT trigger
    print("\nTest 2: High severity (9/10) but non-emergency symptom")
    emr_fields = {
        "chief_complaint": "headache",
        "severity": 9,  # High severity but not emergency symptom
        "duration": "3 days"
    }
    chat_history = [
        {"role": "user", "content": "I have a really bad headache, pain is 9 out of 10"}
    ]
    result = detect_emergency_symptoms_test(emr_fields, chat_history)
    print(f"EMR: {emr_fields}")
    print(f"Emergency detected: {result.get('emergency_flag', False)}")
    print(f"Expected: False (high severity alone should not trigger emergency)")
    
    # Test Case 2b: Severity 8 headache should also NOT trigger
    print("\nTest 2b: Severity 8/10 headache should NOT trigger emergency")
    emr_fields = {
        "chief_complaint": "headache",
        "severity": 8,  # High severity but not emergency symptom
        "duration": "2 hours"
    }
    chat_history = [
        {"role": "user", "content": "I have a headache that's an 8 out of 10 on the pain scale"}
    ]
    result = detect_emergency_symptoms_test(emr_fields, chat_history)
    print(f"EMR: {emr_fields}")
    print(f"Emergency detected: {result.get('emergency_flag', False)}")
    print(f"Expected: False (severity 8 headache should not trigger emergency)")
    
    # Test Case 3: Emergency symptom (difficulty breathing) should trigger
    print("\nTest 3: Emergency symptom (difficulty breathing)")
    emr_fields = {
        "chief_complaint": "shortness of breath",
        "severity": 6,
        "duration": "30 minutes"
    }
    chat_history = [
        {"role": "user", "content": "I'm having trouble breathing and shortness of breath"}
    ]
    result = detect_emergency_symptoms_test(emr_fields, chat_history)
    print(f"EMR: {emr_fields}")
    print(f"Emergency detected: {result.get('emergency_flag', False)}")
    print(f"Expected: True (breathing difficulty is emergency symptom)")
    
    # Test Case 4: Long duration but non-emergency symptom should NOT trigger
    print("\nTest 4: Long duration but non-emergency symptom")
    emr_fields = {
        "chief_complaint": "back pain",
        "severity": 7,
        "duration": "2 weeks"  # Long duration but not emergency
    }
    chat_history = [
        {"role": "user", "content": "I've had back pain for 2 weeks now"}
    ]
    result = detect_emergency_symptoms_test(emr_fields, chat_history)
    print(f"EMR: {emr_fields}")
    print(f"Emergency detected: {result.get('emergency_flag', False)}")
    print(f"Expected: False (duration alone should not trigger emergency)")
    
    # Test Case 5: Multiple emergency symptoms should trigger
    print("\nTest 5: Multiple emergency symptoms")
    emr_fields = {
        "chief_complaint": "chest pain",
        "associated_symptoms": ["shortness of breath", "left arm pain"],
        "severity": 4,  # Low severity but multiple emergency symptoms
        "duration": "10 minutes"
    }
    chat_history = [
        {"role": "user", "content": "I have chest pain and shortness of breath, also pain in my left arm"}
    ]
    result = detect_emergency_symptoms_test(emr_fields, chat_history)
    print(f"EMR: {emr_fields}")
    print(f"Emergency detected: {result.get('emergency_flag', False)}")
    print(f"Expected: True (multiple emergency symptoms)")
    
    print("\n" + "=" * 50)
    print("Test completed. Emergency detection should now be based ONLY on symptom nature,")
    print("not on severity scores or duration.")

if __name__ == "__main__":
    test_emergency_detection()