#!/usr/bin/env python3
"""
Simple test to check for syntax errors
"""

def test_basic_import():
    """Test basic imports"""
    try:
        import json
        import logging
        import os
        from typing import Dict, Any
        print("✅ Basic imports successful")
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_gemini_import():
    """Test Gemini imports"""
    try:
        from google import genai
        from google.genai import types
        print("✅ Gemini imports successful")
        return True
    except Exception as e:
        print(f"❌ Gemini imports failed: {e}")
        return False

def test_pydantic_import():
    """Test Pydantic imports"""
    try:
        from pydantic import BaseModel
        print("✅ Pydantic imports successful")
        return True
    except Exception as e:
        print(f"❌ Pydantic imports failed: {e}")
        return False

def test_gemini_service_import():
    """Test gemini_service import"""
    try:
        import services.gemini_service
        print("✅ Gemini service import successful")
        return True
    except Exception as e:
        print(f"❌ Gemini service import failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 TESTING BASIC IMPORTS AND SYNTAX")
    print("=" * 50)
    
    success = True
    success &= test_basic_import()
    success &= test_gemini_import()
    success &= test_pydantic_import()
    success &= test_gemini_service_import()
    
    if success:
        print("\n🎉 All tests passed! No syntax errors found.")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
        exit(1) 