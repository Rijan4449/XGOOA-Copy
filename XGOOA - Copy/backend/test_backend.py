"""
Backend Test Suite
==================
Comprehensive tests for the invasive species risk prediction backend.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import backend
import json

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_subsection(title):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")

def test_species_list():
    """Test getting species list."""
    print_subsection("Test 1: Get Species List")
    
    species_list = backend.get_species_list()
    print(f"✓ Total species: {len(species_list)}")
    print(f"✓ First 5 species:")
    for i, species in enumerate(species_list[:5], 1):
        print(f"   {i}. {species}")
    
    return len(species_list) > 0

def test_lake_info():
    """Test getting lake information."""
    print_subsection("Test 2: Get Lake Information")
    
    lake_name = "Laguna_de_Bay"
    lake_info = backend.get_lake_info(lake_name)
    
    if lake_info:
        print(f"✓ Lake: {lake_info['name']}")
        print(f"✓ Region: {lake_info['region']}")
        print(f"✓ Coordinates: ({lake_info['latitude']}, {lake_info['longitude']})")
        print(f"✓ Environmental Parameters:")
        for param, value in lake_info['environmental_parameters'].items():
            print(f"   - {param}: {value}")
        return True
    else:
        print(f"✗ Failed to get lake info for {lake_name}")
        return False

def test_most_contributing_feature():
    """Test getting most contributing feature."""
    print_subsection("Test 3: Get Most Contributing Feature")
    
    result = backend.get_most_contributing_feature()
    
    if "error" not in result:
        print(f"✓ Most Contributing Feature: {result['most_contributing_feature']}")
        print(f"✓ Importance Score: {result['importance_score']:.2f}")
        print(f"✓ Percentage: {result['percentage']:.2f}%")
        return True
    else:
        print(f"✗ Error: {result['error']}")
        return False

def test_feature_importance_analysis():
    """Test getting feature importance analysis."""
    print_subsection("Test 4: Get Feature Importance Analysis")
    
    result = backend.get_feature_importance_analysis()
    
    if "error" not in result:
        print(f"✓ Aggregated Importance (Top 6 Parameters):")
        for i, param in enumerate(result['aggregated_importance'], 1):
            print(f"   {i}. {param['parameter']}: {param['total_importance']:.2f} ({param['percentage']:.1f}%)")
        
        print(f"\n✓ Detailed Breakdown (Top 10 Features):")
        for i, detail in enumerate(result['detailed_breakdown'][:10], 1):
            print(f"   {i}. {detail['feature']} ({detail['parameter']}): {detail['importance']:.2f}")
        
        print(f"\n✓ Unmatched Features:")
        print(f"   - Count: {result['unmatched_features']['count']}")
        print(f"   - Total Importance: {result['unmatched_features']['total_importance']:.2f}")
        print(f"   - Percentage: {result['unmatched_features']['percentage']:.1f}%")
        
        return True
    else:
        print(f"✗ Error: {result['error']}")
        return False

def test_risk_predictions():
    """Test getting risk predictions."""
    print_subsection("Test 5: Get Risk Predictions")
    
    test_species = "Anabas testudineus"  # Climbing perch
    print(f"Species: {test_species}")
    print(f"Parameters: temp=27.0°C, pH=7.5, sal=0.5ppt, DO=6.0mg/L, BOD=2.0mg/L, turb=10.0NTU")
    
    result = backend.get_risk_predictions(
        species_name=test_species,
        temperature=27.0,
        ph=7.5,
        salinity=0.5,
        do=6.0,
        bod=2.0,
        turbidity=10.0
    )
    
    if "error" not in result:
        print(f"\n✓ Total Lakes: {len(result['predictions'])}")
        
        print(f"\n✓ Top 5 High-Risk Lakes:")
        for i, pred in enumerate(result['predictions'][:5], 1):
            print(f"   {i}. {pred['lake_name']} ({pred['region']})")
            print(f"      - Adjusted Score: {pred['adjusted_score']:.3f}")
            print(f"      - Risk Level: {pred['risk_level']}")
            print(f"      - Similarity: {pred['similarity']:.3f}")
            print(f"      - Presence: {pred['presence']}")
        
        print(f"\n✓ Risk Level Distribution:")
        risk_counts = {"Low": 0, "Medium": 0, "High": 0}
        for pred in result['predictions']:
            risk_counts[pred['risk_level']] += 1
        for level, count in risk_counts.items():
            print(f"   - {level}: {count} lakes")
        
        if "warning" in result:
            print(f"\n⚠️  Warning: {result['warning']}")
        
        return True
    else:
        print(f"✗ Error: {result['error']}")
        return False

def test_risk_categorization():
    """Test risk categorization function."""
    print_subsection("Test 6: Risk Categorization")
    
    test_scores = [0.1, 0.33, 0.34, 0.5, 0.66, 0.67, 0.9]
    
    print("✓ Testing risk categorization thresholds:")
    for score in test_scores:
        category = backend.categorize_risk(score)
        print(f"   Score {score:.2f} → {category}")
    
    # Verify thresholds
    assert backend.categorize_risk(0.33) == "Low"
    assert backend.categorize_risk(0.34) == "Medium"
    assert backend.categorize_risk(0.66) == "Medium"
    assert backend.categorize_risk(0.67) == "High"
    
    print("✓ All thresholds correct!")
    return True

def test_similarity_calculation():
    """Test environmental similarity calculation."""
    print_subsection("Test 7: Environmental Similarity Calculation")
    
    import numpy as np
    
    # Test cases
    test_cases = [
        {
            "name": "Perfect match",
            "user": [7.5, 0.5, 6.0, 2.0, 10.0, 27.0],
            "lake": [7.5, 0.5, 6.0, 2.0, 10.0, 27.0],
            "expected_sim": 1.0
        },
        {
            "name": "Moderate difference",
            "user": [7.5, 0.5, 6.0, 2.0, 10.0, 27.0],
            "lake": [8.0, 1.0, 7.0, 3.0, 20.0, 28.0],
            "expected_sim": 0.37  # Approximate
        },
        {
            "name": "Large difference",
            "user": [7.5, 0.5, 6.0, 2.0, 10.0, 27.0],
            "lake": [9.0, 5.0, 3.0, 8.0, 100.0, 30.0],
            "expected_sim": 0.05  # Approximate
        }
    ]
    
    print("✓ Testing similarity calculations:")
    for test in test_cases:
        user_env = np.array(test["user"])
        lake_env = np.array(test["lake"])
        similarity = backend.calculate_similarity(user_env, lake_env)
        print(f"   {test['name']}: {similarity:.3f} (expected ~{test['expected_sim']})")
    
    return True

def test_edge_cases():
    """Test edge cases and error handling."""
    print_subsection("Test 8: Edge Cases & Error Handling")
    
    # Test 1: Invalid species
    print("✓ Testing invalid species:")
    result = backend.get_risk_predictions(
        species_name="Invalid Species Name",
        temperature=27.0,
        ph=7.5,
        salinity=0.5,
        do=6.0,
        bod=2.0,
        turbidity=10.0
    )
    if "error" in result:
        print(f"   ✓ Correctly returned error: {result['error']}")
    else:
        print(f"   ✗ Should have returned error")
        return False
    
    # Test 2: Extreme environmental values
    print("\n✓ Testing extreme environmental values:")
    result = backend.get_risk_predictions(
        species_name="Anabas testudineus",
        temperature=50.0,  # Very high
        ph=14.0,           # Maximum pH
        salinity=10.0,     # High salinity
        do=0.0,            # No oxygen
        bod=20.0,          # High BOD
        turbidity=500.0    # Very turbid
    )
    if "error" not in result:
        print(f"   ✓ Successfully handled extreme values")
        if "warning" in result:
            print(f"   ✓ Warning issued: {result['warning']}")
    else:
        print(f"   ✗ Failed with error: {result['error']}")
        return False
    
    return True

def run_all_tests():
    """Run all tests."""
    print_section("BACKEND TEST SUITE")
    
    tests = [
        ("Species List", test_species_list),
        ("Lake Information", test_lake_info),
        ("Most Contributing Feature", test_most_contributing_feature),
        ("Feature Importance Analysis", test_feature_importance_analysis),
        ("Risk Predictions", test_risk_predictions),
        ("Risk Categorization", test_risk_categorization),
        ("Similarity Calculation", test_similarity_calculation),
        ("Edge Cases", test_edge_cases)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print("\nDetailed Results:")
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    run_all_tests()
