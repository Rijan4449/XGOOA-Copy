"""
Example Usage of Invasive Species Risk Prediction Backend
==========================================================
This script demonstrates various ways to use the backend module.
"""

import json
from backend_api import InvasiveSpeciesPredictor

def example_1_basic_prediction():
    """Example 1: Basic single species prediction."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Single Species Prediction")
    print("="*60)
    
    # Initialize predictor
    predictor = InvasiveSpeciesPredictor()
    
    # Make a prediction
    result = predictor.predict_single(
        species="Anabas testudineus",  # Climbing perch
        temperature=27.0,
        ph=7.5,
        salinity=0.0,
        dissolved_oxygen=6.0,
        bod=2.0,
        turbidity=10.0
    )
    
    # Display results
    if result["success"]:
        print(f"\n✓ Prediction for: {result['species']}")
        print(f"  Invasion Probability: {result['invasion_probability']:.4f}")
        print(f"  Invasion Percentage: {result['invasion_percentage']:.2f}%")
        print(f"  Risk Category: {result['risk_category']}")
        print(f"  Risk Color: {result['risk_color']}")
    else:
        print(f"\n✗ Prediction failed: {result['error']}")


def example_2_compare_species():
    """Example 2: Compare invasion risk across multiple species."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Compare Multiple Species")
    print("="*60)
    
    predictor = InvasiveSpeciesPredictor()
    
    # Test species
    test_species = [
        "Anabas testudineus",
        "Danio rerio",
        "Misgurnus anguillicaudatus"
    ]
    
    # Same environmental conditions
    conditions = {
        "temperature": 27.0,
        "ph": 7.5,
        "salinity": 0.0,
        "dissolved_oxygen": 6.0,
        "bod": 2.0,
        "turbidity": 10.0
    }
    
    print(f"\nEnvironmental Conditions:")
    print(f"  Temperature: {conditions['temperature']}°C")
    print(f"  pH: {conditions['ph']}")
    print(f"  Dissolved Oxygen: {conditions['dissolved_oxygen']} mg/L")
    
    print(f"\nComparison Results:")
    print("-" * 60)
    
    results = []
    for species in test_species:
        try:
            result = predictor.predict_single(species=species, **conditions)
            if result["success"]:
                results.append({
                    "species": species,
                    "risk": result["invasion_percentage"],
                    "category": result["risk_category"]
                })
        except:
            continue
    
    # Sort by risk
    results.sort(key=lambda x: x["risk"], reverse=True)
    
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['species']}")
        print(f"   Risk: {r['risk']:.2f}% ({r['category']})")


def example_3_parameter_sensitivity():
    """Example 3: Test sensitivity to temperature changes."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Temperature Sensitivity Analysis")
    print("="*60)
    
    predictor = InvasiveSpeciesPredictor()
    
    species = "Anabas testudineus"
    temperatures = [20.0, 23.0, 26.0, 29.0, 32.0]
    
    print(f"\nSpecies: {species}")
    print(f"Testing temperatures: {temperatures}")
    print("\nResults:")
    print("-" * 60)
    
    for temp in temperatures:
        result = predictor.predict_single(
            species=species,
            temperature=temp,
            ph=7.5,
            salinity=0.0,
            dissolved_oxygen=6.0,
            bod=2.0,
            turbidity=10.0
        )
        
        if result["success"]:
            print(f"Temperature: {temp}°C → Risk: {result['invasion_percentage']:.2f}% ({result['risk_category']})")


def example_4_luzon_lakes_map():
    """Example 4: Generate GeoJSON for Luzon lakes."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Generate Luzon Lakes Map Data")
    print("="*60)
    
    predictor = InvasiveSpeciesPredictor()
    
    # Generate GeoJSON
    geojson = predictor.predict_for_luzon_lakes(
        species="Anabas testudineus",
        temperature=27.0,
        ph=7.5,
        salinity=0.0,
        dissolved_oxygen=6.0,
        bod=2.0,
        turbidity=10.0
    )
    
    print(f"\n✓ Generated GeoJSON with {len(geojson['features'])} lake predictions")
    
    # Display sample predictions
    print("\nSample Lake Predictions:")
    print("-" * 60)
    for feature in geojson['features'][:5]:
        props = feature['properties']
        coords = feature['geometry']['coordinates']
        print(f"{props['name']}")
        print(f"  Location: [{coords[1]:.2f}, {coords[0]:.2f}]")
        print(f"  Risk: {props['percentage']:.2f}% ({props['risk_category']})")
    
    # Save to file
    output_file = "luzon_lakes_predictions.geojson"
    with open(output_file, 'w') as f:
        json.dump(geojson, f, indent=2)
    print(f"\n✓ Saved to: {output_file}")


def example_5_risk_scores_table():
    """Example 5: Generate risk scores table."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Risk Scores Table")
    print("="*60)
    
    predictor = InvasiveSpeciesPredictor()
    
    # Generate table
    df = predictor.get_risk_scores_table(
        temperature=27.0,
        ph=7.5,
        salinity=0.0,
        dissolved_oxygen=6.0,
        bod=2.0,
        turbidity=10.0,
        top_n=10
    )
    
    print("\nTop 10 Species by Invasion Risk:")
    print("-" * 60)
    print(df.to_string(index=False))
    
    # Save to CSV
    output_file = "risk_scores.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved to: {output_file}")


def example_6_species_information():
    """Example 6: Get detailed species information."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Species Information Lookup")
    print("="*60)
    
    predictor = InvasiveSpeciesPredictor()
    
    # Get info for a species
    species = "Anabas testudineus"
    info = predictor.get_species_info(species)
    
    print(f"\nSpecies: {species}")
    print("-" * 60)
    print(f"Common Name: {info.get('common_name')}")
    print(f"Family: {info.get('family')}")
    print(f"Order: {info.get('order')}")
    print(f"Status: {info.get('status')}")
    print(f"Feeding Type: {info.get('feeding_type')}")
    print(f"Trophic Level: {info.get('trophic_level')}")
    print(f"Temperature Range: {info.get('temperature_range')}")
    print(f"Max Length: {info.get('length_max')} cm")
    print(f"Max Weight: {info.get('weight_max')} g")
    print(f"Records in Dataset: {info.get('records_count')}")


def example_7_batch_predictions():
    """Example 7: Batch predictions for multiple scenarios."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Batch Predictions")
    print("="*60)
    
    predictor = InvasiveSpeciesPredictor()
    
    # Define scenarios
    scenarios = [
        {
            "name": "Scenario 1: Optimal conditions",
            "species": "Anabas testudineus",
            "temperature": 27.0,
            "ph": 7.5,
            "salinity": 0.0,
            "dissolved_oxygen": 8.0,
            "bod": 1.0,
            "turbidity": 5.0
        },
        {
            "name": "Scenario 2: Polluted water",
            "species": "Anabas testudineus",
            "temperature": 30.0,
            "ph": 6.5,
            "salinity": 0.0,
            "dissolved_oxygen": 3.0,
            "bod": 8.0,
            "turbidity": 50.0
        },
        {
            "name": "Scenario 3: Cold water",
            "species": "Anabas testudineus",
            "temperature": 18.0,
            "ph": 7.0,
            "salinity": 0.0,
            "dissolved_oxygen": 9.0,
            "bod": 2.0,
            "turbidity": 10.0
        }
    ]
    
    print("\nBatch Prediction Results:")
    print("-" * 60)
    
    for scenario in scenarios:
        name = scenario.pop("name")
        result = predictor.predict_single(**scenario)
        
        if result["success"]:
            print(f"\n{name}")
            print(f"  Temperature: {scenario['temperature']}°C, pH: {scenario['ph']}")
            print(f"  DO: {scenario['dissolved_oxygen']} mg/L, BOD: {scenario['bod']} mg/L")
            print(f"  → Risk: {result['invasion_percentage']:.2f}% ({result['risk_category']})")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("  INVASIVE SPECIES RISK PREDICTION - USAGE EXAMPLES")
    print("="*70)
    
    try:
        example_1_basic_prediction()
        example_2_compare_species()
        example_3_parameter_sensitivity()
        example_4_luzon_lakes_map()
        example_5_risk_scores_table()
        example_6_species_information()
        example_7_batch_predictions()
        
        print("\n" + "="*70)
        print("  All examples completed successfully! ✓")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
