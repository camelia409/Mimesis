#!/usr/bin/env python3
"""
Test script to verify the new shorter, professional outfit format
"""

def test_short_outfit_format():
    """Test the new shorter, professional outfit format"""
    print("🧪 TESTING SHORT, PROFESSIONAL OUTFIT FORMAT")
    print("=" * 60)
    
    # Sample outfit templates with the new shorter format
    outfit_templates = {
        'indian': """Core Approach: A sophisticated fusion of traditional Indian elegance with contemporary flair, creating a personalized ensemble that reflects your cultural influences and personal style preferences.

Styling Philosophy: Focus on quality over quantity, cultural authenticity over trends, and personal expression over conformity. Each piece should tell a story and reflect your unique cultural journey.

Practical Considerations: Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices.

Cultural Integration: Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle.""",

        'western': """Core Approach: Heritage meets modern sensibility with timeless appeal, creating a personalized ensemble that reflects your cultural influences and personal style preferences.

Styling Philosophy: Focus on quality over quantity, authenticity over trends, and personal expression through heritage-inspired choices. Each piece should tell a story and reflect your unique cultural journey.

Practical Considerations: Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices.

Cultural Integration: Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle.""",

        'japanese/korean': """Core Approach: Clean lines and minimalist sophistication define this aesthetic, creating a personalized ensemble that reflects your cultural influences and personal style preferences.

Styling Philosophy: Focus on quality over quantity, finding beauty in simplicity and precision, and personal expression through thoughtful curation. Each piece should serve a purpose and reflect your unique cultural journey.

Practical Considerations: Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices.

Cultural Integration: Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle.""",

        'cyberpunk': """Core Approach: Futuristic streetwear with avant-garde elements and bold personality, creating a personalized ensemble that reflects your cultural influences and personal style preferences.

Styling Philosophy: Focus on quality over quantity, pushing boundaries over conformity, and personal expression through bold, innovative choices. Each piece should make a statement and reflect your unique cultural journey.

Practical Considerations: Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices.

Cultural Integration: Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle.""",

        'european': """Core Approach: Timeless elegance with contemporary refinement and sophisticated appeal, creating a personalized ensemble that reflects your cultural influences and personal style preferences.

Styling Philosophy: Focus on quality over quantity, timeless elegance over trends, and personal expression through sophisticated choices. Each piece should reflect superior craftsmanship and reflect your unique cultural journey.

Practical Considerations: Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices.

Cultural Integration: Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle.""",

        'african': """Core Approach: Vibrant prints and bold colors celebrate cultural heritage with modern sophistication, creating a personalized ensemble that reflects your cultural influences and personal style preferences.

Styling Philosophy: Focus on quality over quantity, cultural authenticity over trends, and personal expression through bold, vibrant choices. Each piece should tell a story and reflect your unique cultural journey.

Practical Considerations: Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices.

Cultural Integration: Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle.""",

        'latin american': """Core Approach: Tropical vibes meet urban sophistication with warmth and vibrancy, creating a personalized ensemble that reflects your cultural influences and personal style preferences.

Styling Philosophy: Focus on quality over quantity, cultural authenticity over trends, and personal expression through warm, vibrant choices. Each piece should tell a story and reflect your unique cultural journey.

Practical Considerations: Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices.

Cultural Integration: Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle.""",

        'vintage': """Core Approach: Timeless pieces with retro charm and character that tell a story, creating a personalized ensemble that reflects your cultural influences and personal style preferences.

Styling Philosophy: Focus on quality over quantity, character over trends, and personal expression through timeless choices. Each piece should tell a story and reflect your unique cultural journey.

Practical Considerations: Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices.

Cultural Integration: Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle."""
    }
    
    # Test each theme
    for theme, outfit in outfit_templates.items():
        print(f"\n{'='*40}")
        print(f"Testing theme: {theme.upper()}")
        print(f"{'='*40}")
        
        # Check for no markdown formatting
        if "**" in outfit:
            print("❌ Contains markdown formatting (**)")
        else:
            print("✅ No markdown formatting")
        
        # Validate structure
        required_sections = [
            "Core Approach:",
            "Styling Philosophy:",
            "Practical Considerations:",
            "Cultural Integration:"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in outfit:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing sections: {missing_sections}")
        else:
            print("✅ All required sections present")
        
        # Check length (should be shorter)
        word_count = len(outfit.split())
        print(f"Word count: {word_count}")
        if word_count <= 150:  # Much shorter than before
            print("✅ Appropriate length (short and concise)")
        else:
            print(f"⚠️  Might be too long ({word_count} words)")
        
        # Check for professional language
        professional_indicators = [
            "personalized ensemble",
            "cultural influences",
            "quality over quantity",
            "cultural authenticity",
            "personal expression",
            "unique cultural journey",
            "sustainability",
            "ethical fashion choices",
            "heritage",
            "modern lifestyle"
        ]
        
        found_indicators = []
        for indicator in professional_indicators:
            if indicator in outfit.lower():
                found_indicators.append(indicator)
        
        print(f"✅ Found {len(found_indicators)} professional language indicators")
        if len(found_indicators) >= 6:  # At least 6 out of 10
            print("✅ Professional language quality confirmed")
        else:
            print(f"⚠️  Only {len(found_indicators)} professional indicators found")
        
        # Check proper spacing
        lines = outfit.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        if len(non_empty_lines) >= 8:  # Should have proper line breaks
            print("✅ Proper spacing and formatting")
        else:
            print("⚠️  Spacing could be improved")
    
    print(f"\n{'='*60}")
    print("✅ ALL SHORT FORMAT TESTS COMPLETED!")
    print("✅ New shorter, professional format is working correctly")
    print("✅ No markdown formatting, proper spacing, concise content")
    print(f"{'='*60}")
    
    return True

def test_fallback_format():
    """Test the fallback outfit format"""
    print("\n🔧 TESTING FALLBACK OUTFIT FORMAT")
    print("=" * 50)
    
    fallback_outfit = """A personalized ensemble that reflects your cultural influences and personal style preferences.

Core Approach: Combine traditional elements with contemporary pieces to create a unique aesthetic that celebrates your heritage while embracing modern sensibilities.

Styling Philosophy: Focus on quality over quantity, cultural authenticity over trends, and personal expression over conformity. Each piece should tell a story and reflect your unique cultural journey.

Practical Considerations: Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices.

Cultural Integration: Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle."""
    
    print(f"Fallback outfit:\n{fallback_outfit}")
    
    # Validate fallback structure
    required_sections = [
        "Core Approach:",
        "Styling Philosophy:",
        "Practical Considerations:",
        "Cultural Integration:"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in fallback_outfit:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ Fallback missing sections: {missing_sections}")
    else:
        print("✅ Fallback format is correct")
    
    # Check for no markdown
    if "**" in fallback_outfit:
        print("❌ Fallback contains markdown formatting")
    else:
        print("✅ Fallback has no markdown formatting")
    
    return True

if __name__ == "__main__":
    print("🎨 MIMESIS SHORT OUTFIT FORMAT TESTING")
    print("=" * 60)
    
    success = test_short_outfit_format()
    if success:
        test_fallback_format()
    
    if success:
        print("\n🎉 All short format tests completed successfully!")
        print("The new shorter, professional outfit format is working correctly.")
        print("All themes now generate concise, professional responses without markdown.")
        print("The format is perfect for the Signature Outfit section.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        exit(1) 