# Invasive Species Risk Prediction Backend

Comprehensive backend module for predicting invasion risk of species across Luzon lakes with environmental similarity weighting and risk categorization.

## 📁 Folder Structure

```
XGOOA/
├── backend/
│   ├── backend.py          # Core backend module with prediction logic
│   ├── flask_api.py        # Flask REST API server
│   ├── README.md           # This file
│   └── __init__.py         # Package initialization
├── model/
│   ├── mooa_xgb_model_v4.json      # Trained XGBoost model
│   └── mooa_preprocessor_v4.joblib # Preprocessing pipeline
├── dataset/
│   └── super_dataset.csv   # Species biological traits + presence data
├── mains/
│   ├── predict.html        # Invasion Risk Map frontend
│   ├── risk_scores.html    # Risk Scores table frontend
│   ├── interpretation.html # Feature importance frontend
│   └── Overview.html       # Overview dashboard frontend
└── assets/
    └── fish_description.csv # Species descriptions for frontend
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pandas numpy xgboost joblib flask flask-cors
```

### 2. Test Backend Module

```bash
cd c:\Users\princ\XGOOA
python backend/backend.py
```

This will run comprehensive tests of all backend functions.

### 3. Start Flask API Server

```bash
python backend/flask_api.py
```

Server will start on `http://localhost:5000`

## 📊 Core Functions

### 1. `get_risk_predictions()`

**Purpose**: Generate invasion risk predictions for all 13 Luzon lakes

**Parameters**:
- `species_name` (str): Name of the invasive species
- `temperature` (float): Water temperature in °C (0-40)
- `ph` (float): Water pH level (0-14)
- `salinity` (float): Salinity in ppt (0-10)
- `do` (float): Dissolved oxygen in mg/L (0-15)
- `bod` (float): Biochemical oxygen demand in mg/L (0-20)
- `turbidity` (float): Turbidity in NTU (0-500)

**Returns**:
```python
{
    "predictions": [
        {
            "lake_name": "Laguna_de_Bay",
            "region": "CALABARZON",
            "latitude": 14.4,
            "longitude": 121.3,
            "raw_score": 0.67,           # Raw model probability
            "adjusted_score": 0.45,      # Probability × similarity
            "risk_level": "Medium",      # "Low", "Medium", or "High"
            "similarity": 0.67,          # Environmental similarity (0-1)
            "presence": "Yes"            # "Yes", "No", or "Unknown"
        },
        # ... 12 more lakes
    ],
    "warning": "..." # Optional warning if inputs differ significantly
}
```

**Algorithm**:
1. Fetch species biological data from dataset
2. Build input DataFrame for all 13 lakes
3. Engineer derived features (temp_pref_range, ph_difference, etc.)
4. Transform data using preprocessor
5. Generate raw predictions using XGBoost model
6. Calculate environmental similarity for each lake
7. Adjust risk scores: `adjusted_score = raw_probability × similarity`
8. Categorize risk levels based on thresholds
9. Check species presence data

**Risk Categorization**:
- 🟢 **Low Risk**: score < 0.34
- 🟡 **Medium Risk**: 0.34 ≤ score < 0.67
- 🔴 **High Risk**: score ≥ 0.67

**Environmental Similarity**:
```python
# 6-dimensional Euclidean distance
distance = ||user_env - lake_env||
similarity = exp(-distance / 10)
```

### 2. `get_most_contributing_feature()`

**Purpose**: Identify THE single most important environmental parameter

**Returns**:
```python
{
    "most_contributing_feature": "BOD",
    "importance_score": 1247.3,
    "percentage": 23.4
}
```

**Algorithm**:
1. Extract feature importances from XGBoost model (gain metric)
2. Map feature indices to names using preprocessor
3. Aggregate importances by 6 core parameters using keyword matching
4. Return parameter with highest total importance

### 3. `get_feature_importance_analysis()`

**Purpose**: Provide detailed aggregated feature importance for Interpretation tab

**Returns**:
```python
{
    "aggregated_importance": [
        {
            "parameter": "BOD",
            "total_importance": 1247.3,
            "feature_count": 8,
            "percentage": 23.4
        },
        # ... 5 more parameters
    ],
    "detailed_breakdown": [
        {
            "parameter": "BOD",
            "feature": "wb_bod_min",
            "importance": 245.6
        },
        # ... more features
    ],
    "unmatched_features": {
        "count": 45,
        "total_importance": 1832.7,
        "percentage": 34.3
    }
}
```

## 🌐 REST API Endpoints

### Health & Info

#### `GET /api/health`
Health check endpoint
```json
{
    "status": "healthy",
    "message": "Invasive Species Prediction API is running",
    "version": "2.0"
}
```

#### `GET /api/info`
Get API information and available endpoints

### Species

#### `GET /api/species`
Get list of all available species
```json
{
    "success": true,
    "count": 43,
    "species": ["Anabas testudineus", "Copella arnoldi", ...]
}
```

### Lakes

#### `GET /api/lakes`
Get list of all Luzon lakes with coordinates

#### `GET /api/lakes/<lake_name>`
Get detailed information about a specific lake

### Predictions

#### `POST /api/predict`
Predict invasion risk for all Luzon lakes

**Request Body**:
```json
{
    "species": "Anabas testudineus",
    "temperature": 27.0,
    "ph": 7.5,
    "salinity": 0.5,
    "dissolved_oxygen": 6.0,
    "bod": 2.0,
    "turbidity": 10.0
}
```

**Response**: See `get_risk_predictions()` return structure

#### `POST /api/geojson`
Get predictions as GeoJSON for map visualization

**Request Body**: Same as `/api/predict`

**Response**:
```json
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [121.3, 14.4]
            },
            "properties": {
                "name": "Laguna_de_Bay",
                "region": "CALABARZON",
                "prob": 0.45,
                "percentage": 45.0,
                "risk_category": "Medium",
                "raw_score": 0.67,
                "similarity": 0.67,
                "presence": "Yes",
                "species": "Anabas testudineus"
            }
        },
        // ... 12 more features
    ]
}
```

### Overview

#### `GET /api/overview/most-contributing`
Get the most contributing environmental feature

### Interpretation

#### `GET /api/interpretation/feature-importance`
Get detailed feature importance analysis

### Risk Scores

#### `POST /api/risk-scores`
Get risk scores table data

**Request Body**: Same as `/api/predict`

**Response**:
```json
{
    "success": true,
    "count": 13,
    "data": [
        {
            "lake": "Laguna_de_Bay",
            "region": "CALABARZON",
            "score": 0.45,
            "risk_level": "Medium",
            "presence": "Yes"
        },
        // ... 12 more lakes
    ]
}
```

## 🗺️ Luzon Lakes Data

The backend includes hardcoded baseline environmental data for 13 Luzon lakes:

| Lake | Region | pH | Salinity | DO | BOD | Turbidity | Temp |
|------|--------|----|---------|----|-----|-----------|------|
| Laguna_de_Bay | CALABARZON | 9.12 | 0.746 | 7.54 | 1.93 | 161.88 | 28.5 |
| Lake_Taal | CALABARZON | 8.32 | 0.85 | 5.61 | 3.82 | 28.0 | 25.5 |
| Sampaloc_Lake | CALABARZON | 7.9 | 0.1 | 3.1 | 8.0 | 28.0 | 27.8 |
| ... | ... | ... | ... | ... | ... | ... | ... |

Each lake includes:
- Environmental parameters (pH, salinity, DO, BOD, turbidity, temperature)
- Geographic coordinates (latitude, longitude)
- Administrative region

## 🔬 Technical Details

### Environmental Similarity Calculation

The backend uses a 6-dimensional Euclidean distance metric to calculate how similar user inputs are to each lake's baseline conditions:

```python
user_env = [ph, salinity, do, bod, turbidity, temperature]
lake_env = [lake_ph, lake_salinity, lake_do, lake_bod, lake_turbidity, lake_temp]

distance = sqrt(sum((user_env[i] - lake_env[i])^2 for i in range(6)))
similarity = exp(-distance / 10)
```

**Interpretation**:
- `similarity = 1.0`: Perfect match (distance = 0)
- `similarity ≈ 0.37`: Moderate difference (distance = 10)
- `similarity ≈ 0.05`: Very different (distance = 30)

### Risk Score Adjustment

Raw model predictions are adjusted based on environmental similarity:

```python
adjusted_score = raw_model_probability × similarity
```

**Rationale**: The model was trained on specific environmental conditions. When user inputs differ significantly from lake baselines, predictions become less reliable. The similarity weighting penalizes predictions for dissimilar conditions.

### Feature Aggregation

The backend aggregates XGBoost feature importances into 6 core environmental parameters using keyword matching:

| Parameter | Keywords |
|-----------|----------|
| pH | `ph`, `_ph_`, `ph_` |
| Salinity | `salinity`, `sal_`, `_sal` |
| Dissolved Oxygen | `_do_`, `_do`, `oxygen`, `dissolved` |
| BOD | `bod`, `_bod_`, `bod_` |
| Turbidity | `turbidity`, `turb_`, `_turb` |
| Temperature | `temp`, `_temp_`, `temp_` |

Features are matched to the first matching parameter. Unmatched features (biological traits, derived features) are tracked separately.

## 🧪 Testing

Run the backend module directly to execute comprehensive tests:

```bash
python backend/backend.py
```

**Test Coverage**:
1. ✅ Get most contributing feature
2. ✅ Get feature importance analysis
3. ✅ Get risk predictions for test species
4. ✅ Get species list
5. ✅ Get lake information

## 🔗 Frontend Integration

### JavaScript Example (Fetch API)

```javascript
// Predict invasion risk
async function predictRisk() {
    const response = await fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            species: 'Anabas testudineus',
            temperature: 27.0,
            ph: 7.5,
            salinity: 0.5,
            dissolved_oxygen: 6.0,
            bod: 2.0,
            turbidity: 10.0
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        console.log('Predictions:', data.predictions);
        // Update map, table, etc.
    }
}

// Get GeoJSON for map
async function loadMapData() {
    const response = await fetch('http://localhost:5000/api/geojson', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            species: 'Anabas testudineus',
            temperature: 27.0,
            ph: 7.5,
            salinity: 0.5,
            dissolved_oxygen: 6.0,
            bod: 2.0,
            turbidity: 10.0
        })
    });
    
    const geojson = await response.json();
    
    // Add to Leaflet map
    L.geoJSON(geojson, {
        pointToLayer: (feature, latlng) => {
            const color = getRiskColor(feature.properties.risk_category);
            return L.circleMarker(latlng, {
                radius: 8,
                fillColor: color,
                fillOpacity: 0.8
            });
        }
    }).addTo(map);
}

function getRiskColor(riskLevel) {
    switch(riskLevel) {
        case 'High': return '#d73027';
        case 'Medium': return '#fee08b';
        case 'Low': return '#1a9850';
        default: return '#999';
    }
}
```

## 📝 Notes

- All numeric values are returned as Python `float` (not numpy types)
- All text values are returned as Python `str`
- The backend automatically handles missing or invalid data
- Presence data is checked against the dataset's waterbody_name column
- The API uses CORS to allow cross-origin requests from the frontend

## 🐛 Error Handling

All functions include comprehensive error handling:

```python
{
    "error": "Species 'Invalid Species' not found in dataset."
}
```

Common errors:
- Species not found
- Missing required parameters
- Invalid parameter values
- Transform failures
- Model prediction errors

## 📚 Dependencies

- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `xgboost`: Machine learning model
- `joblib`: Model serialization
- `flask`: REST API server
- `flask-cors`: Cross-origin resource sharing

## 🔄 Version History

- **v2.0** (2025): Complete rewrite with comprehensive backend module
- **v1.0** (2024): Initial Flask API implementation

## 👥 Authors

XGOOA Team - Invasive Species Risk Prediction System

## 📄 License

Internal use only - XGOOA Project
