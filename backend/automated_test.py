#!/usr/bin/env python3
"""
Automated test script to check the conversation flow
"""

import json
from agent_graph import build_triad_agent, get_missing_fields, REQUIRED_FIELDS

def test_normal_conversation():
    print("🧪 Testing Normal Conversation Flow")
    print("=" * 50)
    
    # Test inputs simulating a normal conversation
    test_inputs = [
        "I have a headache that started this morning",
        "It's been about 6 hours now",
        "I'd rate it about 7 out of 10",
        "It started gradually after I woke up",
        "It's mostly in my forehead and temples",
        "I also feel a bit nauseous and tired",
        "No, no chest pain or breathing problems"
    ]
    
    triage_graph = build_triad_agent()
    session_state = {
        "emr_fields": {},
        "chat_history": [],
        "last_question": None,
        "is_complete": False
    }
    
    for i, user_input in enumerate(test_inputs):
        print(f"\n--- Step {i+1} ---")
        print(f"👤 User: {user_input}")
        
        initial_state = {
            "emr_fields": session_state["emr_fields"],
            "chat_history": session_state["chat_history"],
            "last_question": session_state["last_question"],
            "last_user_input": user_input,
            "is_complete": session_state["is_complete"],
            "next_bot_reply": None
        }
        
        try:
            result = triage_graph.invoke(initial_state)
            
            # Update session state
            session_state["emr_fields"] = result["emr_fields"]
            session_state["chat_history"] = result.get("chat_history", [])
            session_state["last_question"] = result["next_bot_reply"]
            session_state["is_complete"] = result["is_complete"]
            
            print(f"🤖 AI: {result['next_bot_reply']}")
            print(f"📊 EMR Fields: {session_state['emr_fields']}")
            print(f"✅ Complete: {session_state['is_complete']}")
            
            missing = get_missing_fields(session_state["emr_fields"])
            print(f"📋 Missing: {missing}")
            
            if session_state["is_complete"]:
                print("\n🎉 Conversation completed successfully!")
                break
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n📋 Final EMR Data:")
    print(json.dumps(session_state["emr_fields"], indent=2))
    return True

def test_emergency_conversation():
    print("\n🚨 Testing Emergency Detection")
    print("=" * 50)
    
    triage_graph = build_triad_agent()
    
    emergency_inputs = [
        "I have severe chest pain and can't breathe properly",
        "It started suddenly about 10 minutes ago"
    ]
    
    session_state = {
        "emr_fields": {},
        "chat_history": [],
        "last_question": None,
        "is_complete": False
    }
    
    for i, user_input in enumerate(emergency_inputs):
        print(f"\n--- Emergency Step {i+1} ---")
        print(f"👤 User: {user_input}")
        
        initial_state = {
            "emr_fields": session_state["emr_fields"],
            "chat_history": session_state["chat_history"],
            "last_question": session_state["last_question"],
            "last_user_input": user_input,
            "is_complete": session_state["is_complete"],
            "next_bot_reply": None
        }
        
        try:
            result = triage_graph.invoke(initial_state)
            
            session_state["emr_fields"] = result["emr_fields"]
            session_state["is_complete"] = result["is_complete"]
            
            print(f"🤖 AI: {result['next_bot_reply']}")
            print(f"🚨 Emergency Flag: {session_state['emr_fields'].get('emergency_flag', False)}")
            print(f"✅ Complete: {session_state['is_complete']}")
            
            if session_state["emr_fields"].get("emergency_flag"):
                print("✅ Emergency correctly detected!")
                return True
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return False

if __name__ == "__main__":
    print("🧪 AI Triage Backend - Automated Tests")
    print("=" * 60)
    
    # Test normal conversation
    normal_success = test_normal_conversation()
    
    # Test emergency detection
    emergency_success = test_emergency_conversation()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"✅ Normal Conversation: {'PASS' if normal_success else 'FAIL'}")
    print(f"🚨 Emergency Detection: {'PASS' if emergency_success else 'FAIL'}")
    
    if normal_success and emergency_success:
        print("\n🎉 All tests passed! Backend is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")