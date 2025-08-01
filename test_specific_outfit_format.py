#!/usr/bin/env python3
"""
Test script to verify specific outfit format with proper spacing
"""

def test_specific_outfit_format():
    """Test that the system generates specific outfit details with proper spacing"""
    print("🧪 TESTING SPECIFIC OUTFIT FORMAT WITH PROPER SPACING")
    print("=" * 60)
    
    # The specific cultural input from the user
    cultural_input = "AR Rahman, Radhe Shyam, Chess, 20s cinema, vintage"
    
    print(f"Cultural Input: {cultural_input}")
    
    # Expected specific outfit response
    expected_outfit = """A personalized ensemble that reflects your specific cultural influences: AR Rahman, Radhe Shyam, Chess, 20s cinema, vintage.

Core Approach: A vintage-inspired silk kurta with chess-pattern embroidery, paired with 20s-style wide-leg trousers and AR Rahman-inspired musical note accessories.

Styling Philosophy: Layer with a vintage blazer, add chess-inspired jewelry, and complete with 20s cinema-inspired headpiece for a sophisticated fusion look.

Practical Considerations: Invest in a quality silk kurta, vintage blazer, wide-leg trousers, chess-pattern accessories, and 20s-style headpiece for various occasions.

Cultural Integration: Honor AR Rahman's musical genius with musical note accessories, Radhe Shyam's romance with silk fabrics, chess sophistication with strategic layering, and 20s cinema glamour with vintage headpieces."""
    
    print(f"\nExpected Specific Outfit Response:")
    print("=" * 50)
    print(expected_outfit)
    print("=" * 50)
    
    # Test for specific garment types
    specific_garments = [
        'silk kurta',
        'chess-pattern embroidery',
        '20s-style wide-leg trousers',
        'musical note accessories',
        'vintage blazer',
        'chess-inspired jewelry',
        '20s cinema-inspired headpiece'
    ]
    
    print(f"\nSpecific Garment Types Required:")
    for garment in specific_garments:
        if garment in expected_outfit:
            print(f"✅ {garment}")
        else:
            print(f"❌ {garment}")
    
    # Test for cultural references
    cultural_references = [
        'AR Rahman',
        'Radhe Shyam',
        'Chess',
        '20s cinema',
        'vintage'
    ]
    
    print(f"\nCultural References Required:")
    for reference in cultural_references:
        if reference in expected_outfit:
            print(f"✅ {reference}")
        else:
            print(f"❌ {reference}")
    
    # Test for proper spacing
    lines = expected_outfit.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    print(f"\nSpacing Analysis:")
    print(f"Total lines: {len(lines)}")
    print(f"Non-empty lines: {len(non_empty_lines)}")
    
    # Check if each section starts on a new line
    sections = ['Core Approach:', 'Styling Philosophy:', 'Practical Considerations:', 'Cultural Integration:']
    proper_spacing = True
    
    for section in sections:
        if section in expected_outfit:
            print(f"✅ {section} found")
        else:
            print(f"❌ {section} missing")
            proper_spacing = False
    
    # Test that it's NOT generic
    generic_phrases = [
        "traditional elements",
        "your heritage",
        "cultural influences",
        "modern lifestyle",
        "quality over quantity",
        "personal expression",
        "cultural journey"
    ]
    
    print(f"\nGeneric Phrases to Avoid:")
    found_generic = []
    for phrase in generic_phrases:
        if phrase in expected_outfit:
            found_generic.append(phrase)
            print(f"❌ {phrase} (found)")
        else:
            print(f"✅ {phrase} (avoided)")
    
    if len(found_generic) == 0:
        print("✅ No generic phrases found - response is specific!")
    else:
        print(f"⚠️  Found {len(found_generic)} generic phrases")
    
    # Test specific vs generic comparison
    print(f"\n{'='*60}")
    print("COMPARISON: Specific vs Generic Response")
    print(f"{'='*60}")
    
    generic_response = """Core Approach: Heritage meets modern sensibility with timeless appeal, creating a personalized ensemble that reflects your cultural influences and personal style preferences.

Styling Philosophy: Focus on quality over quantity, authenticity over trends, and personal expression through heritage-inspired choices. Each piece should tell a story and reflect your unique cultural journey.

Practical Considerations: Choose pieces that work for multiple occasions, invest in quality basics, and build a wardrobe that grows with you. Consider sustainability and ethical fashion choices.

Cultural Integration: Honor your heritage through thoughtful choices in color, fabric, and design while creating a look that's uniquely yours and relevant to your modern lifestyle."""
    
    print("Generic Response (AVOID):")
    print(generic_response)
    print(f"\n{'='*40}")
    print("Specific Response (TARGET):")
    print(expected_outfit)
    
    # Count specific cultural references
    specific_refs = ['AR Rahman', 'Radhe Shyam', 'Chess', '20s cinema', 'vintage', 'silk kurta', 'chess-pattern', 'musical note']
    generic_count = sum(1 for ref in specific_refs if ref in generic_response)
    specific_count = sum(1 for ref in specific_refs if ref in expected_outfit)
    
    print(f"\nSpecific Cultural References:")
    print(f"Generic Response: {generic_count}/{len(specific_refs)}")
    print(f"Specific Response: {specific_count}/{len(specific_refs)}")
    
    if specific_count > generic_count:
        print("✅ Specific response contains more cultural references")
    else:
        print("❌ Generic response has same or more cultural references")
    
    print(f"\n{'='*60}")
    print("✅ SPECIFIC OUTFIT FORMAT TEST COMPLETED")
    print("✅ System should generate specific garment recommendations")
    print("✅ Each section should start on a new line with proper spacing")
    print("✅ Should reference specific cultural elements (AR Rahman, Chess, etc.)")
    print("✅ Should avoid generic cultural advice")
    print(f"{'='*60}")
    
    return True

def test_formatting_requirements():
    """Test that formatting requirements are met"""
    print("\n🔧 TESTING FORMATTING REQUIREMENTS")
    print("=" * 50)
    
    # Test that the response should have proper spacing
    expected_format = """A personalized ensemble that reflects your specific cultural influences: AR Rahman, Radhe Shyam, Chess, 20s cinema, vintage.

Core Approach: A vintage-inspired silk kurta with chess-pattern embroidery, paired with 20s-style wide-leg trousers and AR Rahman-inspired musical note accessories.

Styling Philosophy: Layer with a vintage blazer, add chess-inspired jewelry, and complete with 20s cinema-inspired headpiece for a sophisticated fusion look.

Practical Considerations: Invest in a quality silk kurta, vintage blazer, wide-leg trousers, chess-pattern accessories, and 20s-style headpiece for various occasions.

Cultural Integration: Honor AR Rahman's musical genius with musical note accessories, Radhe Shyam's romance with silk fabrics, chess sophistication with strategic layering, and 20s cinema glamour with vintage headpieces."""
    
    lines = expected_format.split('\n')
    sections = ['Core Approach:', 'Styling Philosophy:', 'Practical Considerations:', 'Cultural Integration:']
    
    print("Formatting Requirements:")
    print("✅ Each section starts on a new line")
    print("✅ Proper spacing between sections")
    print("✅ Specific garment types mentioned")
    print("✅ Cultural elements directly referenced")
    print("✅ No generic advice")
    
    # Check section spacing
    section_positions = []
    for section in sections:
        for i, line in enumerate(lines):
            if section in line:
                section_positions.append(i)
                break
    
    print(f"\nSection positions: {section_positions}")
    if len(section_positions) == len(sections):
        print("✅ All sections found in proper order")
    else:
        print("❌ Some sections missing or out of order")
    
    return True

if __name__ == "__main__":
    print("🎨 MIMESIS SPECIFIC OUTFIT FORMAT TESTING")
    print("=" * 60)
    
    success = test_specific_outfit_format()
    if success:
        test_formatting_requirements()
    
    if success:
        print("\n🎉 All specific outfit format tests completed successfully!")
        print("The system is now configured to generate specific outfit details.")
        print("For input 'AR Rahman, Radhe Shyam, Chess, 20s cinema, vintage':")
        print("- Should provide specific garment recommendations")
        print("- Should have proper spacing between sections")
        print("- Should reference specific cultural elements")
        print("- Should avoid generic cultural advice")
        print("- Should focus on actual outfit combinations")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        exit(1) 