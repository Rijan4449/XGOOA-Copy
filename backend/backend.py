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

import os
import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
import warnings
from typing import Dict, List, Optional
import io
from PIL import Image
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import base64
from flask import Flask, jsonify

warnings.filterwarnings('ignore')

# ============================================================================
# LOAD RESOURCES
# ============================================================================

# Get the base directory (parent of backend folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load XGBoost models and preprocessors (baseline, OOA, MOOA)

# Baseline model + preprocessor
baseline_model = xgb.XGBClassifier()
baseline_model_path = os.path.join(BASE_DIR, "model", "baseline_model.json")
try:
    baseline_model.load_model(baseline_model_path)
    print(f"✓ Baseline model loaded from {baseline_model_path}")
except Exception as e:
    baseline_model = None
    print(f"⚠ Failed to load baseline model from {baseline_model_path}: {e}")

baseline_preprocessor_path = os.path.join(BASE_DIR, "model", "baseline_preprocessor.joblib")
try:
    baseline_preprocessor = joblib.load(baseline_preprocessor_path)
    print(f"✓ Baseline preprocessor loaded from {baseline_preprocessor_path}")
except Exception as e:
    baseline_preprocessor = None
    print(f"⚠ Failed to load baseline preprocessor from {baseline_preprocessor_path}: {e}")

# OOA model + preprocessor
ooa_model = xgb.XGBClassifier()
ooa_model_path = os.path.join(BASE_DIR, "model", "ooa_model.json")
try:
    ooa_model.load_model(ooa_model_path)
    print(f"✓ OOA model loaded from {ooa_model_path}")
except Exception as e:
    ooa_model = None
    print(f"⚠ Failed to load OOA model from {ooa_model_path}: {e}")

ooa_preprocessor_path = os.path.join(BASE_DIR, "model", "ooa_preprocessor.joblib")
try:
    ooa_preprocessor = joblib.load(ooa_preprocessor_path)
    print(f"✓ OOA preprocessor loaded from {ooa_preprocessor_path}")
except Exception as e:
    ooa_preprocessor = None
    print(f"⚠ Failed to load OOA preprocessor from {ooa_preprocessor_path}: {e}")

# MOOA model + preprocessor (existing filenames preserved)
mooa_model = xgb.XGBClassifier()
mooa_model_path = os.path.join(BASE_DIR, "model", "mooa_xgb_model_v4.json")
try:
    mooa_model.load_model(mooa_model_path)
    print(f"✓ MOOA model loaded from {mooa_model_path}")
except Exception as e:
    mooa_model = None
    print(f"⚠ Failed to load MOOA model from {mooa_model_path}: {e}")

mooa_preprocessor_path = os.path.join(BASE_DIR, "model", "mooa_preprocessor_v4.joblib")
try:
    mooa_preprocessor = joblib.load(mooa_preprocessor_path)
    print(f"✓ MOOA preprocessor loaded from {mooa_preprocessor_path}")
except Exception as e:
    mooa_preprocessor = None
    print(f"⚠ Failed to load MOOA preprocessor from {mooa_preprocessor_path}: {e}")

# Load dataset
dataset_path = os.path.join(BASE_DIR, "dataset", "super_dataset.csv")
super_dataset = pd.read_csv(dataset_path)
print(f"✓ Dataset loaded: {len(super_dataset)} records")

# Hardcoded Luzon lake data with coordinates (Lake Danao removed)
luzon_lakes = pd.DataFrame({
    "Lake Name": [
        "Laguna de Bay", "Lake Taal", "Lake Sampaloc", "Lake Yambo",
        "Lake Pandin", "Lake Mohicap", "Lake Palakpakin", "Lake Nabao",
        "Lake Tadlac", "Lake Tikub", "Lake Buhi", "Lake Bunot"
    ],
    "Region": [
        "IV-A", "IV-A", "IV-A", "IV-A",
        "IV-A", "IV-A", "IV-A", "IV-A",
        "IV-A", "IV-A", "V", "IV-A"
    ],
    "pH": [9.12, 8.32, 7.9, 7.9, 7.8, 7.7, 8.0, 6.33, 7.44, 8.08, 7.95, 7.2],
    "Salinity (ppt)": [0.746, 0.85, 0.1, 0.1, 0.1, 0.1, 0.1, 0.25, 0.361, 0.1, 0.7, 0.1],
    "Dissolved Oxygen (mg/L)": [7.54, 5.61, 3.1, 5.0, 7.3, 4.1, 5.0, 3.14, 7.27, 5.53, 6.89, 7.7],
    "BOD (mg/L)": [1.93, 3.82, 8.0, 2.5, 2.0, 6.8, 3.1, 3.0, 2.33, 2.3, 1.76, 10.2],
    "Turbidity (NTU)": [161.88, 28.0, 28.0, 9.8, 6.5, 10.0, 28.0, 3.5, 3.5, 3.5, 6.18, 9.0],
    "Temperature (°C)": [28.5, 25.5, 27.8, 26.5, 25.8, 26.2, 24.2, 28.0, 29.5, 30.4, 28.5, 28.5],
    "Latitude": [
        14.38333,   # Laguna de Bay - wiki
        13.98550,   # Lake Taal
        14.07848,   # Sampaloc
        14.11860,   # Yambo
        14.11515,   # Pandin (LLDA)
        14.12194,   # Mohicap
        14.11279,   # Palakpakin
        15.238427,  # Nabao Lake (Cabiao)
        14.182179,  # Tadlac
        13.96369,   # Tikub
        13.45000,   # Buhi
        14.08102    # Bunot
    ],
    "Longitude": [
        121.25000,  # Laguna de Bay
        121.00730,  # Lake Taal
        121.33035,  # Sampaloc
        121.36600,  # Yambo
        121.36867,  # Pandin
        121.33444,  # Mohicap
        121.33918,  # Palakpakin
        120.840932, # Nabao Lake
        121.206409, # Tadlac
        121.30597,  # Tikub
        123.51670,  # Buhi
        121.34386   # Bunot
    ]
})


print(f"✓ Luzon lakes data loaded: {len(luzon_lakes)} lakes")


# add constant mappings for presence
print(f"✓ Luzon lakes data loaded: {len(luzon_lakes)} lakes")

# ============================================================================
# CONSTANTS AND MAPPING
# ============================================================================

LUZON_LAKES = [
    "Laguna de Bay", "Lake Taal", "Lake Sampaloc", "Lake Yambo",
    "Lake Pandin", "Lake Mohicap", "Lake Palakpakin", "Lake Nabao",
    "Lake Tadlac", "Lake Tikub", "Lake Buhi", "Lake Bunot"
]

LAKE_NAME_MAPPING = {
    # Laguna de Bay variants
    "Laguna de Bay": "Laguna de Bay",
    "Laguna de Bay, Philippines": "Laguna de Bay",
    "Laguna de Bay, PH": "Laguna de Bay",
    "Laguna de Bay (East Bay)": "Laguna de Bay",
    "Laguna de Bay (Central Bay)": "Laguna de Bay",
    "Laguna de Bay (Station 2)": "Laguna de Bay",
    "Laguna de Bay (Station 3)": "Laguna de Bay",
    "Laguna Lake": "Laguna de Bay",
    "Laguna Lake, Philippines": "Laguna de Bay",
    "Laguna Lake (Laguna)": "Laguna de Bay",

    # Lake Taal variants
    "Taal Lake": "Lake Taal",
    "Lake Taal": "Lake Taal",
    "Lake Taal, Philippines": "Lake Taal",
    "Lake Taal, Batangas": "Lake Taal",
    "Lake Taal (Batangas)": "Lake Taal",
    "Taal Lake, Philippines": "Lake Taal",
    "Taal Freshwater Pond": "Lake Taal",

    # Lake Sampaloc variants
    "Lake Sampaloc": "Lake Sampaloc",
    "Sampaloc Lake": "Lake Sampaloc",
    "Lake Sampaloc, Quezon": "Lake Sampaloc",
    "Lake Sampaloc (San Pablo)": "Lake Sampaloc",
    "Lake Sampaloc, Philippines": "Lake Sampaloc",

    # Lake Buhi variants
    "Lake Buhi": "Lake Buhi",
    "Lake Buhi, Camarines Sur": "Lake Buhi",
    "Lake Buhi, Philippines": "Lake Buhi",
    "Buhi Lake": "Lake Buhi",

    # Lake Yambo variants
    "Lake Yambo": "Lake Yambo",
    "Yambo Lake": "Lake Yambo",
    "Lake Yambo, Laguna": "Lake Yambo",

    # Lake Pandin variants
    "Lake Pandin": "Lake Pandin",
    "Pandin Lake": "Lake Pandin",
    "Lake Pandin, Laguna": "Lake Pandin",

    # Lake Palakpakin variants
    "Lake Palakpakin": "Lake Palakpakin",
    "Palakpakin Lake": "Lake Palakpakin",
    "Lake Palakpakin, Laguna": "Lake Palakpakin",

    # Lake Bunot variants
    "Lake Bunot": "Lake Bunot",
    "Bunot Lake": "Lake Bunot",
    "Lake Bunot, Laguna": "Lake Bunot",

    # Lake Mohicap variants
    "Lake Mohicap": "Lake Mohicap",
    "Mohicap Lake": "Lake Mohicap",

    # Lake Nabao variants
    "Lake Nabao": "Lake Nabao",
    "Nabao Lake": "Lake Nabao",

    # Lake Tadlac variants
    "Lake Tadlac": "Lake Tadlac",
    "Tadlac Lake": "Lake Tadlac",

    # Lake Tikub variants
    "Lake Tikub": "Lake Tikub",
    "Tikub Lake": "Lake Tikub",
}


def normalize_lake_name(lake_name: str) -> Optional[str]:
    if lake_name in LAKE_NAME_MAPPING:
        return LAKE_NAME_MAPPING[lake_name]
    return None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def categorize_risk(score: float) -> str:
    """
    Categorize risk score into Low/Medium/High based on thresholds.
    
    Thresholds:
    - Low Risk: score < 0.33
    - Medium Risk: 0.33 ≤ score < 0.66
    - High Risk: score ≥ 0.66
    
    Args:
        score (float): Risk score between 0 and 1
        
    Returns:
        str: Risk category ("Low", "Medium", or "High")
    """
    if score < 0.33:
        return "Low"
    elif score < 0.66:
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


# update species presence
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
    return "No"

# ============================================================================
# FEATURE IMPORTANCE FUNCTION (ONLY ONE, CLEANED)
# ============================================================================

# ============================================================================ #
# FEATURE IMPORTANCE FIXED
# ============================================================================ #

def get_model_and_preprocessor(model_choice: str = "mooa"):
    if model_choice == "baseline":
        return baseline_model, baseline_preprocessor
    elif model_choice == "ooa":
        return ooa_model, ooa_preprocessor
    return mooa_model, mooa_preprocessor

def get_feature_importance_plots(input_data: pd.DataFrame = None, model_choice: str = "mooa") -> Dict:
    import shap
    model, preprocessor = get_model_and_preprocessor(model_choice)
    if model is None or preprocessor is None:
        raise ValueError(f"Model/preprocessor not available for {model_choice}")

    try:
        # --- ensure required engineered columns exist ---
        required_cols = ["wb_ph_range", "wb_temp_range"]
        if input_data is None:
            input_data = super_dataset.head(100).copy()
        for col in required_cols:
            if col not in input_data.columns:
                input_data[col] = 0.0

        X_processed = preprocessor.transform(input_data)
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_processed)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        feature_names = preprocessor.get_feature_names_out()
        core_feature_groups = {
            'pH': ['num__wb_ph_min', 'num__wb_ph_max'],
            'Salinity': ['num__wb_salinity_min', 'num__wb_salinity_max'],
            'Dissolved Oxygen': ['num__wb_do_min', 'num__wb_do_max'],
            'BOD': ['num__wb_bod_min', 'num__wb_bod_max'],
            'Turbidity': ['num__wb_turbidity_min', 'num__wb_turbidity_max'],
            'Temperature': ['num__wb_temp_min', 'num__wb_temp_max']
        }

        grouped_data = []
        for param, feature_list in core_feature_groups.items():
            valid = [f for f in feature_list if f in feature_names]
            if not valid:
                continue
            idx = [list(feature_names).index(f) for f in valid]
            param_shap = np.abs(shap_values[:, idx]).mean()
            grouped_data.append({
                "parameter": param,
                "total_importance": float(param_shap),
                "feature_count": len(valid),
                "features": ', '.join(valid)
            })

        grouped_data.sort(key=lambda x: x['total_importance'], reverse=True)
        total_importance = sum(g['total_importance'] for g in grouped_data)
        for g in grouped_data:
            g['percentage'] = (g['total_importance'] / total_importance * 100) if total_importance > 0 else 0

        plt.figure(figsize=(8, 5))
        plt.barh([g['parameter'] for g in grouped_data],
                 [g['total_importance'] for g in grouped_data],
                 color='skyblue')
        plt.xlabel("Mean |SHAP value|")
        plt.ylabel("Environmental Parameter")
        plt.title("Environmental Parameter Importance (SHAP)")
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return {"aggregated_importance": grouped_data, "plot_base64": img_base64, "plot_format": "png"}

    except Exception as e:
        raise RuntimeError(f"SHAP analysis failed: {str(e)}")
 
  

# ============================================================================
# MAIN BACKEND FUNCTIONS
# ============================================================================

def get_risk_predictions(species_name: str, temperature: float, ph: float,
                        salinity: float, do: float, bod: float, 
                        turbidity: float, model_choice: str = "mooa") -> Dict:
    """
    Get risk predictions using the selected model.
    Added model_choice parameter to select which model to use.
    """
    try:
        # Get selected model and preprocessor
        model, preprocessor = get_model_and_preprocessor(model_choice)
        
        if model is None or preprocessor is None:
            raise ValueError(f"Model or preprocessor not available for choice: {model_choice}")

        # Get species data and build input DataFrame
        species_row = get_species_data(species_name)
        species_dict = species_row.to_dict()
        
        # Build input DataFrame for all lakes
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
        
        # Engineer derived features
        input_df["temp_pref_range"] = input_df["temp_pref_max"] - input_df["temp_pref_min"]
        input_df["wb_ph_range"] = input_df["wb_ph_max"] - input_df["wb_ph_min"]
        input_df["wb_temp_range"] = input_df["wb_temp_max"] - input_df["wb_temp_min"]
        input_df["temp_in_pref_range"] = (
            (input_df["input_temp"] >= input_df["temp_pref_min"]) & 
            (input_df["input_temp"] <= input_df["temp_pref_max"])
        ).astype(int)
        input_df["fish_ph_pref"] = (input_df["wb_ph_min"] + input_df["wb_ph_max"]) / 2
        input_df["ph_difference"] = abs(input_df["fish_ph_pref"] - input_df["input_ph"])
        
        # Transform and predict using selected model
        X_processed = preprocessor.transform(input_df)
        raw_probabilities = model.predict_proba(X_processed)[:, 1]
        
        # Calculate environmental similarity
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
        
        # Adjust risk scores
        adjusted_scores = raw_probabilities * similarities
        
        # Build results
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
        
        # Check for warning
        result = {"predictions": predictions}
        
        if similarities.max() < 0.05:
            result["warning"] = "Your inputs differ significantly from all lake baselines. Predictions may be unreliable."
        
        return result
        
    except Exception as e:
        return {"error": str(e)}

def build_single_input_row(species: str, temperature: float, ph: float, 
                          salinity: float, dissolved_oxygen: float, 
                          bod: float, turbidity: float) -> pd.DataFrame:
    """
    Builds a single input row DataFrame for model prediction/interpretation.
    """
    try:
        # Get species data and convert Series to DataFrame
        species_data = get_species_data(species)
        if species_data.empty:
            raise ValueError(f"Species '{species}' not found in database")
            
        # Convert Series to DataFrame with a single row
        species_row = pd.DataFrame([species_data])

        # Create input data dictionary
        input_data = {
            "input_temp": temperature,
            "input_ph": ph,
            "input_salinity": salinity,
            "input_do": dissolved_oxygen,
            "input_bod": bod,
            "input_turbidity": turbidity
        }

        # Merge species data with input parameters
        for col in input_data:
            species_row[col] = input_data[col]

        # Add derived features
        species_row["temp_pref_range"] = (
            species_row.get("temp_pref_max", 30) - species_row.get("temp_pref_min", 20)
        )
        species_row["temp_in_pref_range"] = (
            (species_row["input_temp"] >= species_row.get("temp_pref_min", 20)) &
            (species_row["input_temp"] <= species_row.get("temp_pref_max", 30))
        ).astype(int)

        # Handle pH features with fallbacks
        ph_min = species_row.get("ph_min", species_row.get("pH_min", pd.Series([6.0])))
        ph_max = species_row.get("ph_max", species_row.get("pH_max", pd.Series([8.0])))
        species_row["fish_ph_pref"] = (ph_min + ph_max) / 2
        species_row["ph_difference"] = abs(species_row["fish_ph_pref"] - species_row["input_ph"])

        print("Debug - DataFrame shape:", species_row.shape)
        print("Debug - DataFrame columns:", species_row.columns.tolist())

        return species_row

    except Exception as e:
        print(f"Error building input row: {str(e)}")
        print(f"Species data type: {type(species_data)}")
        raise

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