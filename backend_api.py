"""
Invasive Species Risk Prediction Backend Module
================================================
Backend functions for predicting invasion risk of species across Luzon lakes.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class InvasiveSpeciesPredictor:
    """Main class for invasive species risk prediction."""
    
    def __init__(self, 
                 model_path: str = "model/mooa_xgb_model_v4.json",
                 preprocessor_path: str = "model/mooa_preprocessor_v4.joblib",
                 dataset_path: str = "dataset/super_dataset.csv"):
        """Initialize the predictor with model and data paths."""
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.dataset_path = dataset_path
        
        self.model = None
        self.preprocessor = None
        self.dataset = None
        self.species_list = []
        
        self._load_model()
        self._load_preprocessor()
        self._load_dataset()
        
    def _load_model(self):
        """Load the trained XGBoost model from JSON file."""
        try:
            self.model = xgb.Booster()
            self.model.load_model(self.model_path)
            print(f"✓ Model loaded from {self.model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")
    
    def _load_preprocessor(self):
        """Load the preprocessing pipeline from joblib file."""
        try:
            self.preprocessor = joblib.load(self.preprocessor_path)
            print(f"✓ Preprocessor loaded from {self.preprocessor_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load preprocessor: {str(e)}")
    
    def _load_dataset(self):
        """Load and prepare the dataset."""
        try:
            self.dataset = pd.read_csv(self.dataset_path)
            if 'species' in self.dataset.columns:
                self.species_list = sorted(self.dataset['species'].unique().tolist())
            print(f"✓ Dataset loaded: {len(self.dataset)} records, {len(self.species_list)} species")
        except Exception as e:
            raise RuntimeError(f"Failed to load dataset: {str(e)}")
    
    def get_species_list(self) -> List[str]:
        """Get list of all available species."""
        return self.species_list
    
    def get_species_info(self, species_name: str) -> Dict:
        """Get detailed information about a specific species."""
        species_data = self.dataset[self.dataset['species'] == species_name]
        
        if species_data.empty:
            return {"error": f"Species '{species_name}' not found"}
        
        record = species_data.iloc[0]
        
        info = {
            "species": record.get('species', 'Unknown'),
            "common_name": record.get('common_name', 'Unknown'),
            "family": record.get('family', 'Unknown'),
            "order": record.get('order', 'Unknown'),
            "status": record.get('status', 'Unknown'),
            "feeding_type": record.get('feeding_type', 'Unknown'),
            "trophic_level": record.get('trophic_lvl', 'Unknown'),
            "temperature_range": {
                "min": record.get('temp_pref_min', 'Unknown'),
                "max": record.get('temp_pref_max', 'Unknown')
            },
            "length_max": record.get('length_max', 'Unknown'),
            "weight_max": record.get('weight_max', 'Unknown'),
            "records_count": len(species_data)
        }
        
        return info
    
    def prepare_input_features(self, species: str, temperature: float, ph: float,
                               salinity: float, dissolved_oxygen: float, bod: float,
                               turbidity: float) -> pd.DataFrame:
        """Prepare input features for prediction."""
        species_data = self.dataset[self.dataset['species'] == species]
        
        if species_data.empty:
            raise ValueError(f"Species '{species}' not found in dataset")
        
        species_traits = species_data.iloc[0].to_dict()
        
        input_data = {
            'species': species,
            'common_name': species_traits.get('common_name', ''),
            'kingdom': species_traits.get('kingdom', 'Animalia'),
            'phylum': species_traits.get('phylum', 'Chordata'),
            'class': species_traits.get('class', 'Actinopterygii'),
            'order': species_traits.get('order', ''),
            'family': species_traits.get('family', ''),
            'genus': species_traits.get('genus', ''),
            'status': species_traits.get('status', 'established'),
            'feeding_type': species_traits.get('feeding_type', 'other'),
            'temp_max': species_traits.get('temp_max', 30.0),
            'weight_max': species_traits.get('weight_max', 10.0),
            'length_max': species_traits.get('length_max', 10.0),
            'temp_pref_min': species_traits.get('temp_pref_min', 20.0),
            'temp_pref_max': species_traits.get('temp_pref_max', 28.0),
            'temp_range_min': species_traits.get('temp_range_min', 5.0),
            'temp_range_max': species_traits.get('temp_range_max', 5.0),
            'trophic_lvl_estimate_min': species_traits.get('trophic_lvl_estimate_min', 2.5),
            'trophic_lvl_estimate_max': species_traits.get('trophic_lvl_estimate_max', 3.5),
            'trophic_lvl': species_traits.get('trophic_lvl', 3.0),
            'fecundity_mean': species_traits.get('fecundity_mean', 1000.0),
            'fecundity_min': species_traits.get('fecundity_min', 500.0),
            'fecundity_max': species_traits.get('fecundity_max', 2000.0),
            'waterbody_name': 'Laguna de Bay',
            'wb_ph_min': ph,
            'wb_ph_max': ph,
            'wb_salinity_min': salinity,
            'wb_salinity_max': salinity,
            'wb_do_min': dissolved_oxygen,
            'wb_do_max': dissolved_oxygen,
            'wb_bod_min': bod,
            'wb_bod_max': bod,
            'wb_turbidity_min': turbidity,
            'wb_turbidity_max': turbidity,
            'wb_temp_min': temperature,
            'wb_temp_max': temperature
        }
        
        return pd.DataFrame([input_data])
    
    def predict_single(self, species: str, temperature: float, ph: float,
                      salinity: float, dissolved_oxygen: float, bod: float,
                      turbidity: float) -> Dict:
        """Make a single prediction for given parameters."""
        try:
            input_df = self.prepare_input_features(
                species, temperature, ph, salinity, dissolved_oxygen, bod, turbidity
            )
            
            X_processed = self.preprocessor.transform(input_df)
            dmatrix = xgb.DMatrix(X_processed)
            prediction_prob = self.model.predict(dmatrix)[0]
            
            if prediction_prob >= 0.7:
                risk_category = "High Risk"
                risk_color = "#d73027"
            elif prediction_prob >= 0.5:
                risk_category = "Moderate-High Risk"
                risk_color = "#fc8d59"
            elif prediction_prob >= 0.3:
                risk_category = "Moderate Risk"
                risk_color = "#fee08b"
            else:
                risk_category = "Low Risk"
                risk_color = "#91cf60"
            
            return {
                "success": True,
                "species": species,
                "invasion_probability": float(prediction_prob),
                "invasion_percentage": float(prediction_prob * 100),
                "risk_category": risk_category,
                "risk_color": risk_color,
                "input_parameters": {
                    "temperature": temperature,
                    "ph": ph,
                    "salinity": salinity,
                    "dissolved_oxygen": dissolved_oxygen,
                    "bod": bod,
                    "turbidity": turbidity
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def predict_for_luzon_lakes(self, species: str, temperature: float = 27.0,
                                ph: float = 7.5, salinity: float = 0.0,
                                dissolved_oxygen: float = 6.0, bod: float = 2.0,
                                turbidity: float = 10.0) -> Dict:
        """Generate predictions for major Luzon lakes with GeoJSON output."""
        luzon_lakes = [
            {"name": "Laguna de Bay", "lat": 14.4, "lon": 121.25},
            {"name": "Taal Lake", "lat": 14.0, "lon": 120.99},
            {"name": "Lake Lanao", "lat": 7.95, "lon": 124.5},
            {"name": "Naujan Lake", "lat": 13.15, "lon": 121.3},
            {"name": "Lake Buhi", "lat": 13.43, "lon": 123.52},
            {"name": "Lake Bato", "lat": 13.42, "lon": 123.37},
            {"name": "Sampaloc Lake", "lat": 14.13, "lon": 121.28},
            {"name": "Pandin Lake", "lat": 14.12, "lon": 121.29},
            {"name": "Yambo Lake", "lat": 14.14, "lon": 121.27},
            {"name": "Calibato Lake", "lat": 14.11, "lon": 121.30}
        ]
        
        features = []
        
        for lake in luzon_lakes:
            result = self.predict_single(
                species, temperature, ph, salinity, dissolved_oxygen, bod, turbidity
            )
            
            if result["success"]:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lake["lon"], lake["lat"]]
                    },
                    "properties": {
                        "name": lake["name"],
                        "prob": result["invasion_probability"],
                        "percentage": result["invasion_percentage"],
                        "risk_category": result["risk_category"],
                        "species": species
                    }
                }
                features.append(feature)
        
        return {"type": "FeatureCollection", "features": features}
    
    def get_risk_scores_table(self, temperature: float = 27.0, ph: float = 7.5,
                             salinity: float = 0.0, dissolved_oxygen: float = 6.0,
                             bod: float = 2.0, turbidity: float = 10.0,
                             top_n: int = 20) -> pd.DataFrame:
        """Generate risk scores table for multiple species."""
        results = []
        species_to_test = self.species_list[:50] if len(self.species_list) > 50 else self.species_list
        
        for species in species_to_test:
            try:
                result = self.predict_single(
                    species, temperature, ph, salinity, dissolved_oxygen, bod, turbidity
                )
                
                if result["success"]:
                    species_info = self.get_species_info(species)
                    results.append({
                        "Species": species,
                        "Common Name": species_info.get("common_name", "Unknown"),
                        "Family": species_info.get("family", "Unknown"),
                        "Invasion Probability": result["invasion_probability"],
                        "Risk Percentage": f"{result['invasion_percentage']:.1f}%",
                        "Risk Category": result["risk_category"],
                        "Status": species_info.get("status", "Unknown")
                    })
            except:
                continue
        
        df = pd.DataFrame(results)
        df = df.sort_values("Invasion Probability", ascending=False)
        return df.head(top_n)


# Convenience functions
def create_predictor() -> InvasiveSpeciesPredictor:
    """Create and return a predictor instance."""
    return InvasiveSpeciesPredictor()


if __name__ == "__main__":
    print("=" * 60)
    print("Invasive Species Risk Prediction Backend")
    print("=" * 60)
    
    predictor = create_predictor()
    
    print("\n1. Single Species Prediction:")
    result = predictor.predict_single(
        species="Anabas testudineus",
        temperature=27.0, ph=7.5, salinity=0.0,
        dissolved_oxygen=6.0, bod=2.0, turbidity=10.0
    )
    print(f"Species: {result.get('species')}")
    print(f"Invasion Probability: {result.get('invasion_percentage', 0):.2f}%")
    print(f"Risk Category: {result.get('risk_category')}")
    
    print("\n" + "=" * 60)
