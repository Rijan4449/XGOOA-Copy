# backend.py
"""
Invasive Species Risk Prediction Backend Module
================================================
Provides comprehensive backend functionality for invasive species risk prediction
across Luzon lakes with environmental similarity weighting and risk categorization.

Author: XGOOA Team
Version: 1.0
Date: 2025
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import warnings
from typing import Dict, List, Tuple, Optional
import os

warnings.filterwarnings('ignore')

# ============================================================================
# LOAD RESOURCES
# ============================================================================

# Get the base directory (parent of backend folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load XGBoost model
general_model = xgb.XGBClassifier()
model_path = os.path.join(BASE_DIR, "model", "mooa_xgb_model_v4.json")
general_model.load_model(model_path)
print(f"✓ Model loaded from {model_path}")

# Load preprocessor
preprocessor_path = os.path.join(BASE_DIR, "model", "mooa_preprocessor_v4.joblib")
general_preprocessor = joblib.load(preprocessor_path)
print(f"✓ Preprocessor loaded from {preprocessor_path}")

# Load dataset
dataset_path = os.path.join(BASE_DIR, "dataset", "super_dataset.csv")
super_dataset = pd.read_csv(dataset_path)
print(f"✓ Dataset loaded: {len(super_dataset)} records")

# Hardcoded Luzon lake data with coordinates
luzon_lakes = pd.DataFrame({
    "Lake Name": [
        "Laguna_de_Bay", "Lake_Taal", "Sampaloc_Lake", "Yambo_Lake",
        "Pandin_Lake", "Mohicap_Lake", "Palakpakin_Lake", "Nabao_Lake",
        "Tadlac_Lake", "Tikub_Lake", "Lake_Buhi", "Lake_Danao", "Bunot_Lake"
    ],
    "Region": [
        "CALABARZON", "CALABARZON", "CALABARZON", "CALABARZON",
        "CALABARZON", "CALABARZON", "CALABARZON", "CALABARZON",
        "CALABARZON", "CALABARZON", "Bicol", "Leyte", "CALABARZON"
    ],
    "pH": [9.12, 8.32, 7.9, 7.9, 7.8, 7.7, 8.0, 6.33, 7.44, 8.08, 7.95, 7.81, 7.2],
    "Salinity (ppt)": [0.746, 0.85, 0.1, 0.1, 0.1, 0.1, 0.1, 0.25, 0.361, 0.1, 0.7, 0.1, 0.1],
    "Dissolved Oxygen (mg/L)": [7.54, 5.61, 3.1, 5.0, 7.3, 4.1, 5.0, 3.14, 7.27, 5.53, 6.89, 7.15, 7.7],
    "BOD (mg/L)": [1.93, 3.82, 8.0, 2.5, 2.0, 6.8, 3.1, 3.0, 2.33, 2.3, 1.76, 2.49, 10.2],
    "Turbidity (NTU)": [161.88, 28.0, 28.0, 9.8, 6.5, 10.0, 28.0, 3.5, 3.5, 3.5, 6.18, 2.25, 9.0],
    "Temperature (°C)": [28.5, 25.5, 27.8, 26.5, 25.8, 26.2, 24.2, 28.0, 29.5, 30.4, 28.5, 29.5, 28.5],
    "Latitude": [14.4, 14.0, 14.1, 14.15, 14.12, 14.11, 14.13, 14.09, 14.08, 14.16, 13.43, 11.05, 14.14],
    "Longitude": [121.3, 120.98, 121.18, 121.2, 121.19, 121.17, 121.21, 121.16, 121.15, 121.22, 123.52, 124.95, 121.23]
})

print(f"✓ Luzon lakes data loaded: {len(luzon_lakes)} lakes")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def categorize_risk(score: float) -> str:
    """
    Categorize risk score into Low/Medium/High based on thresholds.
    
    Thresholds:
    - Low Risk: score < 0.34
    - Medium Risk: 0.34 ≤ score < 0.67
    - High Risk: score ≥ 0.67
    
    Args:
        score (float): Risk score between 0 and 1
        
    Returns:
        str: Risk category ("Low", "Medium", or "High")
    """
    if score < 0.34:
        return "Low"
    elif score < 0.67:
        return "Medium"
    else:
        return "High"


def calculate_similarity(user_env: np.ndarray, lake_env: np.ndarray) -> float:
    """
    Calculate environmental similarity using exponential decay.
    
    Uses 6-dimensional Euclidean distance with exponential decay:
    similarity = exp(-distance / 10)
    
    Args:
        user_env (np.ndarray): User input environmental parameters [ph, salinity, do, bod, turbidity, temperature]
        lake_env (np.ndarray): Lake baseline environmental parameters
        
    Returns:
        float: Similarity score between 0 and 1
    """
    distance = np.linalg.norm(user_env - lake_env)
    return float(np.exp(-distance / 10))


def get_species_data(species_name: str) -> pd.Series:
    """
    Retrieve species data from the dataset.
    
    Args:
        species_name (str): Name of the species
        
    Returns:
        pd.Series: Species data row
        
    Raises:
        ValueError: If species not found in dataset
    """
    species_row = super_dataset[super_dataset['species'] == species_name]
    
    if species_row.empty:
        raise ValueError(f"Species '{species_name}' not found in dataset.")
    
    return species_row.iloc[0]


def check_species_presence(species_name: str, lake_name: str) -> str:
    """
    Check if a species is present in a specific lake.
    
    Args:
        species_name (str): Name of the species
        lake_name (str): Name of the lake
        
    Returns:
        str: "Yes", "No", or "Unknown"
    """
    # Check if there's presence data in the dataset
    # Look for records where the species matches and waterbody_name matches
    presence_records = super_dataset[
        (super_dataset['species'] == species_name) & 
        (super_dataset['waterbody_name'].str.contains(lake_name.replace('_', ' '), case=False, na=False))
    ]
    
    if not presence_records.empty:
        return "Yes"
    
    # If no direct match, return Unknown (could be enhanced with more sophisticated logic)
    return "Unknown"


# ============================================================================
# MAIN BACKEND FUNCTIONS
# ============================================================================

def get_risk_predictions(species_name: str, temperature: float, ph: float, 
                        salinity: float, do: float, bod: float, turbidity: float) -> Dict:
    """
    Generate invasion risk predictions for all Luzon lakes.
    
    This function:
    1. Fetches species biological data
    2. Builds input DataFrame for all 13 lakes
    3. Engineers derived features required by the preprocessor
    4. Transforms data and generates raw predictions
    5. Calculates environmental similarity for each lake
    6. Adjusts risk scores based on similarity
    7. Categorizes risk levels
    8. Checks species presence data
    
    Args:
        species_name (str): Name of the invasive species
        temperature (float): Water temperature in °C (0-40)
        ph (float): Water pH level (0-14)
        salinity (float): Salinity in ppt (0-10)
        do (float): Dissolved oxygen in mg/L (0-15)
        bod (float): Biochemical oxygen demand in mg/L (0-20)
        turbidity (float): Turbidity in NTU (0-500)
    
    Returns:
        dict: Dictionary containing predictions for all lakes with structure:
            {
                "predictions": [
                    {
                        "lake_name": str,
                        "region": str,
                        "latitude": float,
                        "longitude": float,
                        "raw_score": float,
                        "adjusted_score": float,
                        "risk_level": str,
                        "similarity": float,
                        "presence": str
                    },
                    ...
                ],
                "warning": str (optional, only if max similarity < 0.05)
            }
    """
    try:
        # Step 1: Fetch species data
        species_row = get_species_data(species_name)
        species_dict = species_row.to_dict()
        
        # Step 2: Build input DataFrame for all lakes
        rows = []
        for _, lake in luzon_lakes.iterrows():
            row = {**species_dict}
            row.update({
                "waterbody_name": lake["Lake Name"],
                "wb_ph_min": lake["pH"],
                "wb_ph_max": lake["pH"],
                "wb_salinity_min": lake["Salinity (ppt)"],
                "wb_salinity_max": lake["Salinity (ppt)"],
                "wb_do_min": lake["Dissolved Oxygen (mg/L)"],
                "wb_do_max": lake["Dissolved Oxygen (mg/L)"],
                "wb_bod_min": lake["BOD (mg/L)"],
                "wb_bod_max": lake["BOD (mg/L)"],
                "wb_turbidity_min": lake["Turbidity (NTU)"],
                "wb_turbidity_max": lake["Turbidity (NTU)"],
                "wb_temp_min": lake["Temperature (°C)"],
                "wb_temp_max": lake["Temperature (°C)"],
                "input_temp": temperature,
                "input_ph": ph,
                "input_salinity": salinity,
                "input_do": do,
                "input_bod": bod,
                "input_turbidity": turbidity
            })
            rows.append(row)
        
        input_df = pd.DataFrame(rows)
        
        # Step 3: Engineer derived features
        input_df["temp_pref_range"] = input_df["temp_pref_max"] - input_df["temp_pref_min"]
        input_df["wb_ph_range"] = input_df["wb_ph_max"] - input_df["wb_ph_min"]
        input_df["wb_temp_range"] = input_df["wb_temp_max"] - input_df["wb_temp_min"]
        input_df["temp_in_pref_range"] = (
            (input_df["input_temp"] >= input_df["temp_pref_min"]) & 
            (input_df["input_temp"] <= input_df["temp_pref_max"])
        ).astype(int)
        input_df["fish_ph_pref"] = (input_df["wb_ph_min"] + input_df["wb_ph_max"]) / 2
        input_df["ph_difference"] = abs(input_df["fish_ph_pref"] - input_df["input_ph"])
        
        # Step 4: Transform and predict
        X_processed = general_preprocessor.transform(input_df)
        raw_probabilities = general_model.predict_proba(X_processed)[:, 1]
        
        # Step 5: Calculate environmental similarity
        user_env = np.array([ph, salinity, do, bod, turbidity, temperature])
        similarities = []
        
        for _, lake in luzon_lakes.iterrows():
            lake_env = np.array([
                lake["pH"],
                lake["Salinity (ppt)"],
                lake["Dissolved Oxygen (mg/L)"],
                lake["BOD (mg/L)"],
                lake["Turbidity (NTU)"],
                lake["Temperature (°C)"]
            ])
            similarity = calculate_similarity(user_env, lake_env)
            similarities.append(similarity)
        
        similarities = np.array(similarities)
        
        # Step 6: Adjust risk scores
        adjusted_scores = raw_probabilities * similarities
        
        # Step 7: Build results
        predictions = []
        for i, (_, lake) in enumerate(luzon_lakes.iterrows()):
            prediction = {
                "lake_name": lake["Lake Name"],
                "region": lake["Region"],
                "latitude": float(lake["Latitude"]),
                "longitude": float(lake["Longitude"]),
                "raw_score": float(raw_probabilities[i]),
                "adjusted_score": float(adjusted_scores[i]),
                "risk_level": categorize_risk(adjusted_scores[i]),
                "similarity": float(similarities[i]),
                "presence": check_species_presence(species_name, lake["Lake Name"])
            }
            predictions.append(prediction)
        
        # Sort by adjusted score (descending)
        predictions.sort(key=lambda x: x["adjusted_score"], reverse=True)
        
        # Step 8: Check for warning
        result = {"predictions": predictions}
        
        if similarities.max() < 0.05:
            result["warning"] = "Your inputs differ significantly from all lake baselines. Predictions may be unreliable."
        
        return result
        
    except Exception as e:
        return {"error": str(e)}


def get_most_contributing_feature() -> Dict:
    """
    Identify the single most important environmental parameter.
    
    This function:
    1. Extracts feature importances from the XGBoost model
    2. Maps feature indices to names
    3. Aggregates importances by the 6 core environmental parameters
    4. Returns the parameter with highest total importance
    
    Returns:
        dict: Dictionary with structure:
            {
                "most_contributing_feature": str,  # Parameter name
                "importance_score": float,         # Total gain
                "percentage": float                # Percentage of total importance
            }
    """
    try:
        # Step 1: Extract feature importances
        booster = general_model.get_booster()
        importance_dict = booster.get_score(importance_type='gain')
        
        # Step 2: Map feature indices to names
        try:
            feature_names = general_preprocessor.get_feature_names_out()
            feature_map = {f"f{i}": name for i, name in enumerate(feature_names)}
            
            # Map importances to feature names
            mapped_importance = {}
            for key, value in importance_dict.items():
                if key in feature_map:
                    mapped_importance[feature_map[key]] = value
                else:
                    mapped_importance[key] = value
        except:
            # If mapping fails, use raw feature names
            mapped_importance = importance_dict
        
        # Step 3: Aggregate by 6 core parameters
        core_params = {
            'pH': ['ph', '_ph_', 'ph_'],
            'Salinity': ['salinity', 'sal_', '_sal'],
            'Dissolved Oxygen': ['_do_', '_do', 'oxygen', 'dissolved'],
            'BOD': ['bod', '_bod_', 'bod_'],
            'Turbidity': ['turbidity', 'turb_', '_turb'],
            'Temperature': ['temp', '_temp_', 'temp_']
        }
        
        param_importance = {param: 0.0 for param in core_params.keys()}
        
        for feature_name, importance in mapped_importance.items():
            feature_lower = feature_name.lower()
            matched = False
            
            for param, keywords in core_params.items():
                if any(keyword in feature_lower for keyword in keywords):
                    param_importance[param] += importance
                    matched = True
                    break
        
        # Step 4: Find parameter with highest importance
        total_importance = sum(param_importance.values())
        
        if total_importance == 0:
            return {
                "error": "No feature importance data available",
                "most_contributing_feature": "Unknown",
                "importance_score": 0.0,
                "percentage": 0.0
            }
        
        most_important_param = max(param_importance.items(), key=lambda x: x[1])
        
        return {
            "most_contributing_feature": most_important_param[0],
            "importance_score": float(most_important_param[1]),
            "percentage": float((most_important_param[1] / total_importance) * 100)
        }
        
    except Exception as e:
        return {"error": str(e)}


def get_feature_importance_analysis() -> Dict:
    """
    Analyze feature importance aggregated by the 6 core environmental parameters.
    
    This function:
    1. Extracts and maps feature importances
    2. Aggregates by the 6 core parameters
    3. Tracks detailed breakdown of which features contribute to each parameter
    4. Identifies unmatched features
    5. Sorts by total importance
    
    Returns:
        dict: Dictionary with structure:
            {
                "aggregated_importance": [
                    {
                        "parameter": str,
                        "total_importance": float,
                        "feature_count": int,
                        "percentage": float
                    },
                    ...
                ],
                "detailed_breakdown": [
                    {
                        "parameter": str,
                        "feature": str,
                        "importance": float
                    },
                    ...
                ],
                "unmatched_features": {
                    "count": int,
                    "total_importance": float,
                    "percentage": float
                }
            }
    """
    try:
        # Step 1: Extract feature importances
        booster = general_model.get_booster()
        importance_dict = booster.get_score(importance_type='gain')
        
        # Step 2: Map feature indices to names
        try:
            feature_names = general_preprocessor.get_feature_names_out()
            feature_map = {f"f{i}": name for i, name in enumerate(feature_names)}
            
            mapped_importance = {}
            for key, value in importance_dict.items():
                if key in feature_map:
                    mapped_importance[feature_map[key]] = value
                else:
                    mapped_importance[key] = value
        except:
            mapped_importance = importance_dict
        
        # Step 3: Aggregate by 6 core parameters
        core_params = {
            'pH': ['ph', '_ph_', 'ph_'],
            'Salinity': ['salinity', 'sal_', '_sal'],
            'Dissolved Oxygen': ['_do_', '_do', 'oxygen', 'dissolved'],
            'BOD': ['bod', '_bod_', 'bod_'],
            'Turbidity': ['turbidity', 'turb_', '_turb'],
            'Temperature': ['temp', '_temp_', 'temp_']
        }
        
        param_data = {param: {'total': 0.0, 'features': [], 'count': 0} for param in core_params.keys()}
        unmatched_features = []
        
        for feature_name, importance in mapped_importance.items():
            feature_lower = feature_name.lower()
            matched = False
            
            for param, keywords in core_params.items():
                if any(keyword in feature_lower for keyword in keywords):
                    param_data[param]['total'] += importance
                    param_data[param]['features'].append({
                        'feature': feature_name,
                        'importance': float(importance)
                    })
                    param_data[param]['count'] += 1
                    matched = True
                    break
            
            if not matched:
                unmatched_features.append({
                    'feature': feature_name,
                    'importance': float(importance)
                })
        
        # Calculate totals
        total_matched = sum(data['total'] for data in param_data.values())
        total_unmatched = sum(f['importance'] for f in unmatched_features)
        grand_total = total_matched + total_unmatched
        
        # Step 4: Build aggregated importance list
        aggregated = []
        for param, data in param_data.items():
            if data['total'] > 0:  # Only include parameters with importance
                aggregated.append({
                    "parameter": param,
                    "total_importance": float(data['total']),
                    "feature_count": data['count'],
                    "percentage": float((data['total'] / grand_total) * 100) if grand_total > 0 else 0.0
                })
        
        # Sort by total importance (descending)
        aggregated.sort(key=lambda x: x['total_importance'], reverse=True)
        
        # Step 5: Build detailed breakdown
        detailed_breakdown = []
        for param, data in param_data.items():
            for feature_info in data['features']:
                detailed_breakdown.append({
                    "parameter": param,
                    "feature": feature_info['feature'],
                    "importance": feature_info['importance']
                })
        
        # Sort detailed breakdown by importance (descending)
        detailed_breakdown.sort(key=lambda x: x['importance'], reverse=True)
        
        # Step 6: Build unmatched features summary
        unmatched_summary = {
            "count": len(unmatched_features),
            "total_importance": float(total_unmatched),
            "percentage": float((total_unmatched / grand_total) * 100) if grand_total > 0 else 0.0
        }
        
        return {
            "aggregated_importance": aggregated,
            "detailed_breakdown": detailed_breakdown[:50],  # Limit to top 50 for performance
            "unmatched_features": unmatched_summary
        }
        
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_species_list() -> List[str]:
    """
    Get list of all available species in the dataset.
    
    Returns:
        list: Sorted list of species names
    """
    return sorted(super_dataset['species'].unique().tolist())


def get_lake_info(lake_name: str) -> Optional[Dict]:
    """
    Get detailed information about a specific lake.
    
    Args:
        lake_name (str): Name of the lake
        
    Returns:
        dict: Lake information or None if not found
    """
    lake_data = luzon_lakes[luzon_lakes['Lake Name'] == lake_name]
    
    if lake_data.empty:
        return None
    
    lake = lake_data.iloc[0]
    return {
        "name": lake["Lake Name"],
        "region": lake["Region"],
        "latitude": float(lake["Latitude"]),
        "longitude": float(lake["Longitude"]),
        "environmental_parameters": {
            "pH": float(lake["pH"]),
            "salinity_ppt": float(lake["Salinity (ppt)"]),
            "dissolved_oxygen_mgL": float(lake["Dissolved Oxygen (mg/L)"]),
            "bod_mgL": float(lake["BOD (mg/L)"]),
            "turbidity_ntu": float(lake["Turbidity (NTU)"]),
            "temperature_c": float(lake["Temperature (°C)"])
        }
    }


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("INVASIVE SPECIES RISK PREDICTION BACKEND - TEST MODE")
    print("=" * 70)
    
    # Test 1: Get most contributing feature
    print("\n1. Testing get_most_contributing_feature()...")
    result = get_most_contributing_feature()
    if "error" not in result:
        print(f"   Most Contributing Feature: {result['most_contributing_feature']}")
        print(f"   Importance Score: {result['importance_score']:.2f}")
        print(f"   Percentage: {result['percentage']:.2f}%")
    else:
        print(f"   Error: {result['error']}")
    
    # Test 2: Get feature importance analysis
    print("\n2. Testing get_feature_importance_analysis()...")
    result = get_feature_importance_analysis()
    if "error" not in result:
        print(f"   Top 3 Parameters:")
        for i, param in enumerate(result['aggregated_importance'][:3], 1):
            print(f"      {i}. {param['parameter']}: {param['total_importance']:.2f} ({param['percentage']:.1f}%)")
        print(f"   Unmatched Features: {result['unmatched_features']['count']} ({result['unmatched_features']['percentage']:.1f}%)")
    else:
        print(f"   Error: {result['error']}")
    
    # Test 3: Get risk predictions
    print("\n3. Testing get_risk_predictions()...")
    test_species = "Anabas testudineus"  # Climbing perch
    result = get_risk_predictions(
        species_name=test_species,
        temperature=27.0,
        ph=7.5,
        salinity=0.5,
        do=6.0,
        bod=2.0,
        turbidity=10.0
    )
    
    if "error" not in result:
        print(f"   Species: {test_species}")
        print(f"   Total Lakes: {len(result['predictions'])}")
        print(f"   Top 3 High-Risk Lakes:")
        for i, pred in enumerate(result['predictions'][:3], 1):
            print(f"      {i}. {pred['lake_name']}: {pred['adjusted_score']:.3f} ({pred['risk_level']})")
        if "warning" in result:
            print(f"   ⚠️  {result['warning']}")
    else:
        print(f"   Error: {result['error']}")
    
    # Test 4: Get species list
    print("\n4. Testing get_species_list()...")
    species_list = get_species_list()
    print(f"   Total Species: {len(species_list)}")
    print(f"   First 5 Species: {species_list[:5]}")
    
    # Test 5: Get lake info
    print("\n5. Testing get_lake_info()...")
    lake_info = get_lake_info("Laguna_de_Bay")
    if lake_info:
        print(f"   Lake: {lake_info['name']}")
        print(f"   Region: {lake_info['region']}")
        print(f"   Coordinates: ({lake_info['latitude']}, {lake_info['longitude']})")
        print(f"   pH: {lake_info['environmental_parameters']['pH']}")
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70 + "\n")
