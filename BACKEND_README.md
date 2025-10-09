# Invasive Species Risk Prediction - Backend Module

## Overview

This backend module provides Python functions for predicting invasion risk of invasive species across Luzon lakes using a trained XGBoost model. It's designed to integrate seamlessly with the existing frontend UI.

## Features

- ✅ Load trained XGBoost model and preprocessor
- ✅ Single species risk prediction
- ✅ Batch predictions for multiple species
- ✅ GeoJSON generation for Luzon lakes map visualization
- ✅ Risk scores table generation
- ✅ Species information retrieval
- ✅ REST API endpoints for frontend integration
- ✅ SHAP values for model interpretation (optional)

## Project Structure

```
XGOOA/
├── backend_api.py              # Core prediction module
├── flask_server.py             # Flask REST API server
├── requirements.txt            # Python dependencies
├── model/
│   ├── mooa_xgb_model_v4.json         # Trained XGBoost model
│   └── mooa_preprocessor_v4.joblib    # Preprocessing pipeline
├── dataset/
│   └── super_dataset.csv              # Species and waterbody data
└─��� mains/
    └── predict.html                   # Frontend UI
```

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Model Files

Ensure these files exist:
- `model/mooa_xgb_model_v4.json`
- `model/mooa_preprocessor_v4.joblib`
- `dataset/super_dataset.csv`

## Usage

### Option 1: Direct Python Usage

```python
from backend_api import InvasiveSpeciesPredictor

# Initialize predictor
predictor = InvasiveSpeciesPredictor()

# Make a single prediction
result = predictor.predict_single(
    species="Anabas testudineus",
    temperature=27.0,
    ph=7.5,
    salinity=0.0,
    dissolved_oxygen=6.0,
    bod=2.0,
    turbidity=10.0
)

print(f"Invasion Probability: {result['invasion_percentage']:.2f}%")
print(f"Risk Category: {result['risk_category']}")

# Generate GeoJSON for Luzon lakes
geojson = predictor.predict_for_luzon_lakes(
    species="Anabas testudineus",
    temperature=27.0,
    ph=7.5
)

# Get risk scores table
risk_table = predictor.get_risk_scores_table(
    temperature=27.0,
    ph=7.5,
    top_n=20
)
print(risk_table)
```

### Option 2: Flask API Server

Start the API server:

```bash
python flask_server.py
```

The server will run on `http://localhost:5000`

## API Endpoints

### 1. Health Check
```
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "message": "Invasive Species Prediction API is running"
}
```

### 2. Get All Species
```
GET /api/species
```

Response:
```json
{
  "success": true,
  "count": 43,
  "species": ["Anabas testudineus", "Copella arnoldi", ...]
}
```

### 3. Get Species Information
```
GET /api/species/<species_name>
```

Response:
```json
{
  "success": true,
  "data": {
    "species": "Anabas testudineus",
    "common_name": "Climbing perch",
    "family": "Anabantidae",
    "status": "invasive",
    "feeding_type": "predator",
    "temperature_range": {"min": 22.0, "max": 30.0}
  }
}
```

### 4. Single Prediction
```
POST /api/predict
Content-Type: application/json

{
  "species": "Anabas testudineus",
  "temperature": 27.0,
  "ph": 7.5,
  "salinity": 0.0,
  "dissolved_oxygen": 6.0,
  "bod": 2.0,
  "turbidity": 10.0
}
```

Response:
```json
{
  "success": true,
  "species": "Anabas testudineus",
  "invasion_probability": 0.85,
  "invasion_percentage": 85.0,
  "risk_category": "High Risk",
  "risk_color": "#d73027",
  "input_parameters": {...}
}
```

### 5. Luzon Lakes Prediction (GeoJSON)
```
POST /api/predict/luzon-lakes
Content-Type: application/json

{
  "species": "Anabas testudineus",
  "temperature": 27.0,
  "ph": 7.5,
  "salinity": 0.0,
  "dissolved_oxygen": 6.0,
  "bod": 2.0,
  "turbidity": 10.0
}
```

Response:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [121.25, 14.4]
      },
      "properties": {
        "name": "Laguna de Bay",
        "prob": 0.85,
        "percentage": 85.0,
        "risk_category": "High Risk",
        "species": "Anabas testudineus"
      }
    },
    ...
  ]
}
```

### 6. Risk Scores Table
```
POST /api/risk-scores
Content-Type: application/json

{
  "temperature": 27.0,
  "ph": 7.5,
  "salinity": 0.0,
  "dissolved_oxygen": 6.0,
  "bod": 2.0,
  "turbidity": 10.0,
  "top_n": 20
}
```

Response:
```json
{
  "success": true,
  "count": 20,
  "data": [
    {
      "Species": "Anabas testudineus",
      "Common Name": "Climbing perch",
      "Family": "Anabantidae",
      "Invasion Probability": 0.85,
      "Risk Percentage": "85.0%",
      "Risk Category": "High Risk",
      "Status": "invasive"
    },
    ...
  ]
}
```

### 7. Overview Statistics
```
GET /api/overview
```

Response:
```json
{
  "success": true,
  "data": {
    "total_species": 43,
    "total_records": 1234,
    "model_type": "XGBoost Classifier",
    "model_version": "v4",
    "status_distribution": {
      "invasive": 15,
      "established": 20,
      "reported": 8
    },
    "risk_distribution": {
      "high_risk": 150,
      "moderate_risk": 500,
      "low_risk": 584
    }
  }
}
```

## Frontend Integration

### Update predict.html

Replace the external GeoJSON URL with your API endpoint:

```javascript
// In predict.html, update this line:
const EXTERNAL_GEOJSON_URL = "http://localhost:5000/api/predict/luzon-lakes";

// Update the loadPoints function to use POST:
async function loadPoints({ useFormParams = false } = {}) {
  try {
    const data = useFormParams ? {
      species: document.getElementById('specie').value,
      temperature: parseFloat(document.getElementById('temperature').value),
      ph: parseFloat(document.getElementById('water_ph').value),
      salinity: parseFloat(document.getElementById('salinity').value),
      dissolved_oxygen: parseFloat(document.getElementById('dissolved_oxygen').value),
      bod: parseFloat(document.getElementById('bod').value),
      turbidity: parseFloat(document.getElementById('turbidity').value)
    } : {
      species: "Anabas testudineus",
      temperature: 27.0,
      ph: 7.5,
      salinity: 0.0,
      dissolved_oxygen: 6.0,
      bod: 2.0,
      turbidity: 10.0
    };
    
    const res = await fetch(EXTERNAL_GEOJSON_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (!res.ok) throw new Error("Bad response");
    const geojson = await res.json();
    renderPoints(geojson);
  } catch (err) {
    console.error("Error loading predictions:", err);
  }
}
```

## Class Reference

### InvasiveSpeciesPredictor

Main class for handling predictions.

#### Methods

- `__init__(model_path, preprocessor_path, dataset_path)` - Initialize predictor
- `get_species_list()` - Get list of all species
- `get_species_info(species_name)` - Get species details
- `predict_single(species, temperature, ph, salinity, dissolved_oxygen, bod, turbidity)` - Single prediction
- `predict_for_luzon_lakes(species, ...)` - Generate GeoJSON for Luzon lakes
- `get_risk_scores_table(temperature, ph, ..., top_n)` - Generate risk scores table
- `calculate_shap_values(species, ...)` - Calculate SHAP values (requires shap library)

## Risk Categories

| Probability | Category | Color |
|------------|----------|-------|
| ≥ 0.7 | High Risk | #d73027 (Red) |
| 0.5 - 0.7 | Moderate-High Risk | #fc8d59 (Orange) |
| 0.3 - 0.5 | Moderate Risk | #fee08b (Yellow) |
| < 0.3 | Low Risk | #91cf60 (Green) |

## Input Parameters

| Parameter | Unit | Range | Description |
|-----------|------|-------|-------------|
| temperature | °C | 0-50 | Water temperature |
| ph | - | 0-14 | Water pH level |
| salinity | ppt | 0-50 | Salinity (parts per thousand) |
| dissolved_oxygen | mg/L | 0-20 | Dissolved oxygen concentration |
| bod | mg/L | 0-10 | Biochemical oxygen demand |
| turbidity | NTU | 0-250 | Water turbidity |

## Testing

Run the backend module directly to test:

```bash
python backend_api.py
```

This will:
1. Load the model and data
2. Run example predictions
3. Generate sample outputs

## Troubleshooting

### Model Loading Error
- Verify `model/mooa_xgb_model_v4.json` exists
- Check XGBoost version compatibility

### Preprocessor Error
- Verify `model/mooa_preprocessor_v4.joblib` exists
- Ensure scikit-learn version matches training version

### Species Not Found
- Check species name spelling
- Use `get_species_list()` to see available species

### CORS Error (Frontend)
- Ensure Flask-CORS is installed
- Check API server is running on correct port

## Performance Notes

- First prediction may be slower (model loading)
- Subsequent predictions are fast (~10-50ms)
- Batch predictions are optimized
- Consider caching for frequently requested species

## Future Enhancements

- [ ] Add SHAP interpretation endpoint
- [ ] Implement caching for predictions
- [ ] Add batch prediction endpoint
- [ ] Support custom waterbody parameters
- [ ] Add model confidence intervals
- [ ] Implement prediction history logging

## Support

For issues or questions:
1. Check this README
2. Review error messages in console
3. Verify all dependencies are installed
4. Check model files are present

## License

This module is part of the XGOOA Invasive Species Risk Prediction System.

---

**Version:** 1.0  
**Last Updated:** 2024  
**Authors:** XGOOA Team
