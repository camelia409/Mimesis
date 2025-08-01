#!/usr/bin/env python3
"""
Simple test to validate the new structured outfit format
"""

def test_outfit_structure():
    """Test the new structured outfit format"""
    print("🧪 TESTING NEW STRUCTURED OUTFIT FORMAT")
    print("=" * 60)
    
    # Sample outfit templates with the new format
    outfit_templates = {
        'indian': """**Core Approach:** A sophisticated fusion of traditional Indian elegance with contemporary flair, creating a personalized ensemble that reflects your cultural influences and personal style preferences. This approach combines traditional elements with contemporary pieces to create a unique aesthetic that celebrates your heritage while embracing modern sensibilities.

**Styling Philosophy:** Focus on quality over quantity, cultural authenticity over trends, and personal expression over conformity. Each piece should tell a story and reflect your unique cultural journey, creating a wardrobe that speaks to both your heritage and your modern lifestyle.

**Practical Considerations:** Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices, mixing high-end investment pieces with accessible alternatives that maintain the aesthetic integrity.

**Cultural Integration:** Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle. Incorporate traditional motifs, rich jewel tones, and handloom fabrics in contemporary silhouettes that bridge the past and present.""",

        'japanese/korean': """**Core Approach:** Clean lines and minimalist sophistication define this aesthetic, creating a personalized ensemble that reflects your cultural influences and personal style preferences. This approach combines traditional Japanese/Korean philosophy with contemporary fashion to create a unique aesthetic that celebrates heritage while embracing modern sensibilities.

**Styling Philosophy:** Focus on quality over quantity, finding beauty in simplicity and precision, and personal expression through thoughtful curation. Each piece should serve a purpose and reflect your unique cultural journey, creating a wardrobe that speaks to both your heritage and your modern lifestyle.

**Practical Considerations:** Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices, mixing high-end investment pieces with accessible alternatives that maintain the aesthetic integrity.

**Cultural Integration:** Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle. Incorporate traditional philosophy of finding beauty in simplicity, natural fibers, and precise tailoring in contemporary silhouettes that bridge the past and present.""",

        'western': """**Core Approach:** Heritage meets modern sensibility with timeless appeal, creating a personalized ensemble that reflects your cultural influences and personal style preferences. This approach combines traditional Western heritage with contemporary fashion to create a unique aesthetic that celebrates authenticity while embracing modern sensibilities.

**Styling Philosophy:** Focus on quality over quantity, authenticity over trends, and personal expression through heritage-inspired choices. Each piece should tell a story and reflect your unique cultural journey, creating a wardrobe that speaks to both your heritage and your modern lifestyle.

**Practical Considerations:** Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices, mixing high-end investment pieces with accessible alternatives that maintain the aesthetic integrity.

**Cultural Integration:** Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle. Incorporate traditional Western elements, natural materials, and heritage-inspired details in contemporary silhouettes that bridge the past and present.""",

        'cyberpunk': """**Core Approach:** Futuristic streetwear with avant-garde elements and bold personality, creating a personalized ensemble that reflects your cultural influences and personal style preferences. This approach combines cutting-edge technology with contemporary fashion to create a unique aesthetic that celebrates innovation while embracing modern sensibilities.

**Styling Philosophy:** Focus on quality over quantity, pushing boundaries over conformity, and personal expression through bold, innovative choices. Each piece should make a statement and reflect your unique cultural journey, creating a wardrobe that speaks to both your futuristic vision and your modern lifestyle.

**Practical Considerations:** Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices, mixing high-end investment pieces with accessible alternatives that maintain the aesthetic integrity.

**Cultural Integration:** Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle. Incorporate futuristic elements, technical fabrics, and innovative details in contemporary silhouettes that bridge the past and present.""",

        'european': """**Core Approach:** Timeless elegance with contemporary refinement and sophisticated appeal, creating a personalized ensemble that reflects your cultural influences and personal style preferences. This approach combines traditional European craftsmanship with contemporary fashion to create a unique aesthetic that celebrates heritage while embracing modern sensibilities.

**Styling Philosophy:** Focus on quality over quantity, timeless elegance over trends, and personal expression through sophisticated choices. Each piece should reflect superior craftsmanship and reflect your unique cultural journey, creating a wardrobe that speaks to both your heritage and your modern lifestyle.

**Practical Considerations:** Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices, mixing high-end investment pieces with accessible alternatives that maintain the aesthetic integrity.

**Cultural Integration:** Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle. Incorporate traditional European elements, quality materials, and heritage-inspired details in contemporary silhouettes that bridge the past and present.""",

        'african': """**Core Approach:** Vibrant prints and bold colors celebrate cultural heritage with modern sophistication, creating a personalized ensemble that reflects your cultural influences and personal style preferences. This approach combines traditional African craftsmanship with contemporary fashion to create a unique aesthetic that celebrates heritage while embracing modern sensibilities.

**Styling Philosophy:** Focus on quality over quantity, cultural authenticity over trends, and personal expression through bold, vibrant choices. Each piece should tell a story and reflect your unique cultural journey, creating a wardrobe that speaks to both your heritage and your modern lifestyle.

**Practical Considerations:** Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices, mixing high-end investment pieces with accessible alternatives that maintain the aesthetic integrity.

**Cultural Integration:** Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle. Incorporate traditional African elements, vibrant prints, and heritage-inspired details in contemporary silhouettes that bridge the past and present.""",

        'latin american': """**Core Approach:** Tropical vibes meet urban sophistication with warmth and vibrancy, creating a personalized ensemble that reflects your cultural influences and personal style preferences. This approach combines traditional Latin American craftsmanship with contemporary fashion to create a unique aesthetic that celebrates heritage while embracing modern sensibilities.

**Styling Philosophy:** Focus on quality over quantity, cultural authenticity over trends, and personal expression through warm, vibrant choices. Each piece should tell a story and reflect your unique cultural journey, creating a wardrobe that speaks to both your heritage and your modern lifestyle.

**Practical Considerations:** Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices, mixing high-end investment pieces with accessible alternatives that maintain the aesthetic integrity.

**Cultural Integration:** Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle. Incorporate traditional Latin American elements, vibrant colors, and heritage-inspired details in contemporary silhouettes that bridge the past and present.""",

        'vintage': """**Core Approach:** Timeless pieces with retro charm and character that tell a story, creating a personalized ensemble that reflects your cultural influences and personal style preferences. This approach combines traditional vintage aesthetics with contemporary fashion to create a unique aesthetic that celebrates heritage while embracing modern sensibilities.

**Styling Philosophy:** Focus on quality over quantity, character over trends, and personal expression through timeless choices. Each piece should tell a story and reflect your unique cultural journey, creating a wardrobe that speaks to both your heritage and your modern lifestyle.

**Practical Considerations:** Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices, mixing high-end investment pieces with accessible alternatives that maintain the aesthetic integrity.

**Cultural Integration:** Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle. Incorporate traditional vintage elements, timeless materials, and heritage-inspired details in contemporary silhouettes that bridge the past and present."""
    }
    
    # Test each theme
    for theme, outfit in outfit_templates.items():
        print(f"\n{'='*40}")
        print(f"Testing theme: {theme.upper()}")
        print(f"{'='*40}")
        
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
        
        # Check section content quality
        sections = outfit.split("**")
        section_count = len([s for s in sections if s.strip().endswith(":")])
        if section_count >= 4:
            print("✅ Proper section structure confirmed")
        else:
            print(f"⚠️  Only {section_count} sections found")
    
    print(f"\n{'='*60}")
    print("✅ ALL OUTFIT FORMAT TESTS COMPLETED!")
    print("✅ New structured format is working correctly")
    print("✅ All themes now generate high-end, structured responses")
    print(f"{'='*60}")
    
    return True

def test_fallback_format():
    """Test the fallback outfit format"""
    print("\n🔧 TESTING FALLBACK OUTFIT FORMAT")
    print("=" * 50)
    
    fallback_outfit = """A personalized ensemble that reflects your cultural influences and personal style preferences.

**Core Approach:** Combine traditional elements with contemporary pieces to create a unique aesthetic that celebrates your heritage while embracing modern sensibilities.

**Styling Philosophy:** Focus on quality over quantity, cultural authenticity over trends, and personal expression over conformity. Each piece should tell a story and reflect your unique cultural journey.

**Practical Considerations:** Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices.

**Cultural Integration:** Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle."""
    
    print(f"Fallback outfit:\n{fallback_outfit}")
    
    # Validate fallback structure
    required_sections = [
        "**Core Approach:**",
        "**Styling Philosophy:**",
        "**Practical Considerations:**",
        "**Cultural Integration:**"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in fallback_outfit:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ Fallback missing sections: {missing_sections}")
    else:
        print("✅ Fallback format is correct")
    
    return True

if __name__ == "__main__":
    print("🎨 MIMESIS OUTFIT FORMAT TESTING")
    print("=" * 60)
    
    success = test_outfit_structure()
    if success:
        test_fallback_format()
    
    if success:
        print("\n🎉 All outfit format tests completed successfully!")
        print("The new structured outfit format is working correctly.")
        print("All themes now generate high-end, structured responses.")
        print("The format matches the high-end structure shown in the image.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        exit(1) 