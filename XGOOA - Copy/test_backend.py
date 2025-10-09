"""
Test Script for Invasive Species Risk Prediction Backend
=========================================================
Run this script to verify the backend module is working correctly.
"""

import sys
import json
from backend_api import InvasiveSpeciesPredictor

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_model_loading():
    """Test 1: Model and data loading."""
    print_section("TEST 1: Model and Data Loading")
    try:
        predictor = InvasiveSpeciesPredictor()
        print("✓ Model loaded successfully")
        print("✓ Preprocessor loaded successfully")
        print("✓ Dataset loaded successfully")
        print(f"\nDataset Info:")
        print(f"  - Total records: {len(predictor.dataset)}")
        print(f"  - Total species: {len(predictor.species_list)}")
        print(f"  - Sample species: {predictor.species_list[:5]}")
        return predictor
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None

def test_species_info(predictor):
    """Test 2: Species information retrieval."""
    print_section("TEST 2: Species Information Retrieval")
    try:
        # Test with a known species
        test_species = predictor.species_list[0] if predictor.species_list else "Anabas testudineus"
        info = predictor.get_species_info(test_species)
        
        print(f"✓ Retrieved info for: {test_species}")
        print(f"\nSpecies Details:")
        print(f"  - Common Name: {info.get('common_name')}")
        print(f"  - Family: {info.get('family')}")
        print(f"  - Status: {info.get('status')}")
        print(f"  - Feeding Type: {info.get('feeding_type')}")
        print(f"  - Temperature Range: {info.get('temperature_range')}")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_single_prediction(predictor):
    """Test 3: Single species prediction."""
    print_section("TEST 3: Single Species Prediction")
    try:
        test_species = predictor.species_list[0] if predictor.species_list else "Anabas testudineus"
        
        result = predictor.predict_single(
            species=test_species,
            temperature=27.0,
            ph=7.5,
            salinity=0.0,
            dissolved_oxygen=6.0,
            bod=2.0,
            turbidity=10.0
        )
        
        if result.get("success"):
            print(f"✓ Prediction successful for: {test_species}")
            print(f"\nPrediction Results:")
            print(f"  - Invasion Probability: {result['invasion_probability']:.4f}")
            print(f"  - Invasion Percentage: {result['invasion_percentage']:.2f}%")
            print(f"  - Risk Category: {result['risk_category']}")
            print(f"  - Risk Color: {result['risk_color']}")
            return True
        else:
            print(f"✗ Prediction failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_luzon_lakes_prediction(predictor):
    """Test 4: Luzon lakes GeoJSON generation."""
    print_section("TEST 4: Luzon Lakes GeoJSON Generation")
    try:
        test_species = predictor.species_list[0] if predictor.species_list else "Anabas testudineus"
        
        geojson = predictor.predict_for_luzon_lakes(
            species=test_species,
            temperature=27.0,
            ph=7.5,
            salinity=0.0,
            dissolved_oxygen=6.0,
            bod=2.0,
            turbidity=10.0
        )
        
        print(f"✓ GeoJSON generated for: {test_species}")
        print(f"\nGeoJSON Info:")
        print(f"  - Type: {geojson.get('type')}")
        print(f"  - Number of features: {len(geojson.get('features', []))}")
        
        if geojson.get('features'):
            first_feature = geojson['features'][0]
            print(f"\nSample Feature:")
            print(f"  - Lake: {first_feature['properties']['name']}")
            print(f"  - Probability: {first_feature['properties']['prob']:.4f}")
            print(f"  - Risk Category: {first_feature['properties']['risk_category']}")
            print(f"  - Coordinates: {first_feature['geometry']['coordinates']}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_risk_scores_table(predictor):
    """Test 5: Risk scores table generation."""
    print_section("TEST 5: Risk Scores Table Generation")
    try:
        df = predictor.get_risk_scores_table(
            temperature=27.0,
            ph=7.5,
            salinity=0.0,
            dissolved_oxygen=6.0,
            bod=2.0,
            turbidity=10.0,
            top_n=5
        )
        
        print(f"✓ Risk scores table generated")
        print(f"\nTop 5 Species by Risk:")
        print(df.to_string(index=False))
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_multiple_predictions(predictor):
    """Test 6: Multiple predictions with different parameters."""
    print_section("TEST 6: Multiple Predictions (Parameter Variation)")
    try:
        test_species = predictor.species_list[0] if predictor.species_list else "Anabas testudineus"
        
        test_cases = [
            {"temp": 20.0, "ph": 6.5, "desc": "Cool, acidic water"},
            {"temp": 27.0, "ph": 7.5, "desc": "Neutral conditions"},
            {"temp": 32.0, "ph": 8.5, "desc": "Warm, alkaline water"}
        ]
        
        print(f"Testing species: {test_species}\n")
        
        for i, case in enumerate(test_cases, 1):
            result = predictor.predict_single(
                species=test_species,
                temperature=case["temp"],
                ph=case["ph"],
                salinity=0.0,
                dissolved_oxygen=6.0,
                bod=2.0,
                turbidity=10.0
            )
            
            if result.get("success"):
                print(f"Case {i} - {case['desc']}:")
                print(f"  Temperature: {case['temp']}°C, pH: {case['ph']}")
                print(f"  → Risk: {result['invasion_percentage']:.2f}% ({result['risk_category']})")
            else:
                print(f"Case {i} failed: {result.get('error')}")
        
        print("\n✓ Multiple predictions completed")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  INVASIVE SPECIES RISK PREDICTION - BACKEND TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Test 1: Model loading
    predictor = test_model_loading()
    results.append(("Model Loading", predictor is not None))
    
    if predictor is None:
        print("\n✗ Cannot continue tests - model loading failed")
        return
    
    # Test 2: Species info
    results.append(("Species Info", test_species_info(predictor)))
    
    # Test 3: Single prediction
    results.append(("Single Prediction", test_single_prediction(predictor)))
    
    # Test 4: Luzon lakes
    results.append(("Luzon Lakes GeoJSON", test_luzon_lakes_prediction(predictor)))
    
    # Test 5: Risk scores
    results.append(("Risk Scores Table", test_risk_scores_table(predictor)))
    
    # Test 6: Multiple predictions
    results.append(("Multiple Predictions", test_multiple_predictions(predictor)))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is ready for integration.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
    
    print("=" * 70 + "\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {str(e)}")
        sys.exit(1)
