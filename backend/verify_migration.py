#!/usr/bin/env python3
"""
Verification script for TTS microservice migration
"""

import os
import sys
from pathlib import Path

def check_files_removed():
    """Check that old TTS files have been removed"""
    print("🔍 Checking removed files...")
    
    removed_items = [
        "TTS/",
        "TTS/file.py"
    ]
    
    all_removed = True
    for item in removed_items:
        if os.path.exists(item):
            print(f"  ❌ {item} still exists (should be removed)")
            all_removed = False
        else:
            print(f"  ✅ {item} removed")
    
    return all_removed

def check_new_files():
    """Check that new TTS integration files exist"""
    print("\n🔍 Checking new files...")
    
    new_files = [
        "tts_client.py",
        "test_tts.py",
        "TTS_INTEGRATION.md"
    ]
    
    all_exist = True
    for file in new_files:
        if os.path.exists(file):
            print(f"  ✅ {file} created")
        else:
            print(f"  ❌ {file} missing")
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Check that dependencies have been updated"""
    print("\n🔍 Checking dependencies...")
    
    # Check requirements.txt
    req_ok = True
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            content = f.read()
            if "elevenlabs" in content:
                print("  ❌ elevenlabs still in requirements.txt")
                req_ok = False
            else:
                print("  ✅ elevenlabs removed from requirements.txt")
    
    # Check pyproject.toml
    pyproject_ok = True
    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "r") as f:
            content = f.read()
            if "elevenlabs" in content:
                print("  ❌ elevenlabs still in pyproject.toml")
                pyproject_ok = False
            else:
                print("  ✅ elevenlabs removed from pyproject.toml")
    
    return req_ok and pyproject_ok

def check_env_config():
    """Check environment configuration"""
    print("\n🔍 Checking environment configuration...")
    
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            content = f.read()
            if "TTS_SERVICE_URL" in content:
                print("  ✅ TTS_SERVICE_URL configured in .env")
                return True
            else:
                print("  ❌ TTS_SERVICE_URL missing from .env")
                return False
    else:
        print("  ❌ .env file not found")
        return False

def check_main_py_integration():
    """Check that main.py has been updated with TTS integration"""
    print("\n🔍 Checking main.py integration...")
    
    if not os.path.exists("main.py"):
        print("  ❌ main.py not found")
        return False
    
    with open("main.py", "r") as f:
        content = f.read()
    
    checks = [
        ("tts_client import", "from tts_client import tts_client"),
        ("TTS endpoint", "@app.post(\"/tts\")"),
        ("Audio endpoint", "@app.get(\"/audio/{filename}\")"),
        ("Chat TTS endpoint", "@app.post(\"/chat/tts\")"),
        ("TTS health endpoint", "@app.get(\"/tts/health\")"),
        ("Triage TTS endpoint", "@app.post(\"/triage/text/tts\")")
    ]
    
    all_good = True
    for check_name, check_string in checks:
        if check_string in content:
            print(f"  ✅ {check_name} found")
        else:
            print(f"  ❌ {check_name} missing")
            all_good = False
    
    return all_good

def main():
    print("=" * 50)
    print("TTS MICROSERVICE MIGRATION VERIFICATION")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("Files removed", check_files_removed),
        ("New files created", check_new_files),
        ("Dependencies updated", check_dependencies),
        ("Environment configured", check_env_config),
        ("Main.py integration", check_main_py_integration)
    ]
    
    results = []
    for check_name, check_func in checks:
        result = check_func()
        results.append((check_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("MIGRATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("\nNext steps:")
        print("1. Make sure your TTS microservice is running on port 9003")
        print("2. Start the FastAPI server: uvicorn main:app --reload")
        print("3. Run tests: python test_tts.py")
    else:
        print("⚠️  MIGRATION INCOMPLETE - Please fix the issues above")
    
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())