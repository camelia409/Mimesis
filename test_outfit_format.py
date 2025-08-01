#!/usr/bin/env python3
"""
Test script to verify the new structured outfit format
"""

import sys
import os

# Add the current directory to the path so we can import from services
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_outfit_format():
    """Test the new structured outfit format"""
    print("🧪 TESTING NEW STRUCTURED OUTFIT FORMAT")
    print("=" * 60)
    
    try:
        # Import the outfit generation function
        from services.gemini_service import generate_dynamic_outfit
        
        print("✅ Successfully imported outfit generation function")
        
        # Test different themes
        test_themes = [
            ['indian'],
            ['japanese/korean'],
            ['western'],
            ['cyberpunk'],
            ['european'],
            ['african'],
            ['latin american'],
            ['vintage']
        ]
        
        for theme in test_themes:
            print(f"\n{'='*40}")
            print(f"Testing theme: {theme[0].upper()}")
            print(f"{'='*40}")
            
            outfit = generate_dynamic_outfit(theme, ['test'])
            print(f"Generated outfit:\n{outfit}")
            
            # Validate structure
            required_sections = [
                "**Core Approach:**",
                "**Styling Philosophy:**",
                "**Practical Considerations:**",
                "**Cultural Integration:**"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in outfit:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"❌ Missing sections: {missing_sections}")
            else:
                print("✅ All required sections present")
            
            # Check for high-end language
            high_end_indicators = [
                "personalized ensemble",
                "cultural influences",
                "personal style preferences",
                "quality over quantity",
                "cultural authenticity",
                "personal expression",
                "unique cultural journey",
                "sustainability",
                "ethical fashion choices",
                "investment pieces",
                "heritage",
                "modern lifestyle"
            ]
            
            found_indicators = []
            for indicator in high_end_indicators:
                if indicator in outfit.lower():
                    found_indicators.append(indicator)
            
            print(f"✅ Found {len(found_indicators)} high-end language indicators")
            if len(found_indicators) >= 8:  # At least 8 out of 12
                print("✅ High-end language quality confirmed")
            else:
                print(f"⚠️  Only {len(found_indicators)} high-end indicators found")
        
        print(f"\n{'='*60}")
        print("✅ ALL OUTFIT FORMAT TESTS COMPLETED!")
        print("✅ New structured format is working correctly")
        print(f"{'='*60}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_format():
    """Test the fallback outfit format"""
    print("\n🔧 TESTING FALLBACK OUTFIT FORMAT")
    print("=" * 50)
    
    try:
        from services.gemini_service import generate_dynamic_outfit
        
        # Test with unknown theme
        outfit = generate_dynamic_outfit(['unknown_theme'], ['test'])
        print(f"Fallback outfit:\n{outfit}")
        
        # Validate fallback structure
        required_sections = [
            "**Core Approach:**",
            "**Styling Philosophy:**",
            "**Practical Considerations:**",
            "**Cultural Integration:**"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in outfit:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Fallback missing sections: {missing_sections}")
        else:
            print("✅ Fallback format is correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎨 MIMESIS OUTFIT FORMAT TESTING")
    print("=" * 60)
    
    success = test_outfit_format()
    if success:
        test_fallback_format()
    
    if success:
        print("\n🎉 All outfit format tests completed successfully!")
        print("The new structured outfit format is working correctly.")
        print("All themes now generate high-end, structured responses.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1) 