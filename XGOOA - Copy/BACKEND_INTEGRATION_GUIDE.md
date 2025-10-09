# Backend Integration Guide

Complete guide for integrating the XGOOA backend with your existing frontend.

## 📁 Complete Folder Structure

```
XGOOA/
├── backend/                          # ✨ NEW: Backend module
│   ├── __init__.py                   # Package initialization
│   ├── backend.py                    # Core backend logic
│   ├── flask_api.py                  # REST API server
│   ├── test_backend.py               # Comprehensive test suite
│   ├── README.md                     # Detailed documentation
│   └── QUICKSTART.md                 # Quick start guide
│
├── model/                            # Machine learning models
│   ├── mooa_xgb_model_v4.json       # Trained XGBoost model
│   └── mooa_preprocessor_v4.joblib  # Preprocessing pipeline
│
├── dataset/                          # Data files
│   └── super_dataset.csv            # Species traits + presence data
│
├── mains/                            # Frontend HTML pages
│   ├── Overview.html                # Overview dashboard
│   ├── predict.html                 # Invasion Risk Map
│   ├── interpretation.html          # Feature importance (SHAP)
│   └── risk_scores.html             # Risk scores table
│
├── assets/                           # Static assets
│   ├── fish_description.csv         # Species descriptions
│   ├── logo.png
│   ├── icon.png
│   └── background.jpg
│
├── includes/                         # Shared components
│   └── sidebar.html                 # Navigation sidebar
│
├── start/                            # Authentication pages
│   ├── login.html
│   ├── signup.html
│   └── ...
│
├── index.html                        # Landing page
├── style.css                         # Global styles
├── predict.css                       # Predict page styles
├── risk_score.css                    # Risk scores styles
├── interpretation.css                # Interpretation styles
├── Overview.css                      # Overview styles
│
└── BACKEND_INTEGRATION_GUIDE.md     # This file
```

## 🔄 Data Flow

```
┌─────────────────┐
│   Frontend      │
│   (HTML/JS)     │
└────────┬────────┘
         │
         │ HTTP Request (POST /api/predict)
         │ {species, temperature, ph, ...}
         ▼
┌─────────────────┐
│   Flask API     │
│  (flask_api.py) │
└────────┬────────┘
         │
         │ Function Call
         │ get_risk_predictions(...)
         ▼
┌─────────────────┐
│   Backend       │
│  (backend.py)   │
├─────────────────┤
│ 1. Load species │
│ 2. Build input  │
│ 3. Transform    │
│ 4. Predict      │
│ 5. Calculate    │
│    similarity   │
│ 6. Adjust scores│
│ 7. Categorize   │
└────────┬────────┘
         │
         │ Return predictions
         ▼
┌─────────────────┐
│   Frontend      │
│   Updates UI    │
│ - Map markers   │
│ - Risk table    │
│ - Charts        │
└─────────────────┘
```

## 🎯 Backend Functions → Frontend Pages

### 1. Overview Tab (`Overview.html`)

**Backend Function**: `get_most_contributing_feature()`

**Returns**:
```json
{
    "most_contributing_feature": "BOD",
    "importance_score": 1247.3,
    "percentage": 23.4
}
```

**Frontend Integration**:
```javascript
fetch('http://localhost:5000/api/overview/most-contributing')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('most-contributing').textContent = 
                data.data.most_contributing_feature;
        }
    });
```

### 2. Invasion Risk Map (`predict.html`)

**Backend Function**: `get_risk_predictions()` → GeoJSON endpoint

**Returns**:
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
                "prob": 0.45,
                "risk_category": "Medium",
                ...
            }
        }
    ]
}
```

**Frontend Integration**:
```javascript
async function loadMapData() {
    const payload = {
        species: document.getElementById('specie').value,
        temperature: parseFloat(document.getElementById('temperature').value),
        ph: parseFloat(document.getElementById('water_ph').value),
        salinity: parseFloat(document.getElementById('salinity').value),
        dissolved_oxygen: parseFloat(document.getElementById('dissolved_oxygen').value),
        bod: parseFloat(document.getElementById('bod').value),
        turbidity: parseFloat(document.getElementById('turbidity').value)
    };
    
    const response = await fetch('http://localhost:5000/api/geojson', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    const geojson = await response.json();
    
    // Add to Leaflet map
    L.geoJSON(geojson, {
        pointToLayer: (feature, latlng) => {
            return L.circleMarker(latlng, {
                radius: 8,
                fillColor: getRiskColor(feature.properties.risk_category),
                fillOpacity: 0.85
            }).bindPopup(`
                <b>${feature.properties.name}</b><br/>
                Risk: ${(feature.properties.prob * 100).toFixed(1)}%<br/>
                Level: ${feature.properties.risk_category}
            `);
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

### 3. Interpretation Tab (`interpretation.html`)

**Backend Function**: `get_feature_importance_analysis()`

**Returns**:
```json
{
    "aggregated_importance": [
        {
            "parameter": "BOD",
            "total_importance": 1247.3,
            "feature_count": 8,
            "percentage": 23.4
        },
        ...
    ],
    "detailed_breakdown": [...],
    "unmatched_features": {...}
}
```

**Frontend Integration**:
```javascript
fetch('http://localhost:5000/api/interpretation/feature-importance')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Create bar chart with Chart.js or similar
            const labels = data.data.aggregated_importance.map(p => p.parameter);
            const values = data.data.aggregated_importance.map(p => p.percentage);
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Feature Importance (%)',
                        data: values,
                        backgroundColor: '#0d3b66'
                    }]
                }
            });
        }
    });
```

### 4. Risk Scores Tab (`risk_scores.html`)

**Backend Function**: `get_risk_predictions()` → Risk scores endpoint

**Returns**:
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
        ...
    ]
}
```

**Frontend Integration**:
```javascript
function loadRiskScores() {
    const tbody = document.getElementById("risk-score-table-body");
    
    const payload = {
        species: document.getElementById('specie').value,
        temperature: parseFloat(document.getElementById('temperature').value),
        ph: parseFloat(document.getElementById('water_ph').value),
        salinity: parseFloat(document.getElementById('salinity').value),
        dissolved_oxygen: parseFloat(document.getElementById('dissolved_oxygen').value),
        bod: parseFloat(document.getElementById('bod').value),
        turbidity: parseFloat(document.getElementById('turbidity').value)
    };
    
    fetch('http://localhost:5000/api/risk-scores', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            tbody.innerHTML = data.data.map(row => `
                <tr>
                    <td>${row.lake}</td>
                    <td>${row.region}</td>
                    <td>${row.score.toFixed(3)}</td>
                    <td><span class="badge bg-${getRiskBadge(row.risk_level)}">${row.risk_level}</span></td>
                    <td>${row.presence === 'Yes' ? '✓' : row.presence === 'No' ? '✗' : '?'}</td>
                </tr>
            `).join('');
        }
    });
}

function getRiskBadge(level) {
    return level === 'High' ? 'danger' : level === 'Medium' ? 'warning' : 'success';
}
```

## 🔑 Key Concepts

### Risk Categorization

The backend uses these thresholds for risk levels:

```python
def categorize_risk(score):
    if score < 0.34:
        return "Low"      # 🟢 Green
    elif score < 0.67:
        return "Medium"   # 🟡 Yellow
    else:
        return "High"     # 🔴 Red
```

### Environmental Similarity

The backend calculates how similar user inputs are to each lake's baseline:

```python
# 6-dimensional Euclidean distance
user_env = [ph, salinity, do, bod, turbidity, temperature]
lake_env = [lake_ph, lake_sal, lake_do, lake_bod, lake_turb, lake_temp]

distance = sqrt(sum((user_env[i] - lake_env[i])^2))
similarity = exp(-distance / 10)
```

**Interpretation**:
- `similarity = 1.0`: Perfect match
- `similarity = 0.37`: Moderate difference (distance = 10)
- `similarity = 0.05`: Very different (distance = 30)

### Adjusted Risk Score

The final risk score is adjusted based on environmental similarity:

```python
adjusted_score = raw_model_probability × similarity
```

This penalizes predictions when user inputs differ significantly from lake baselines.

## 🚀 Deployment Steps

### Step 1: Test Backend Locally

```bash
cd c:\Users\princ\XGOOA
python backend/test_backend.py
```

### Step 2: Start Flask Server

```bash
python backend/flask_api.py
```

### Step 3: Update Frontend API URLs

In each HTML file, update the API base URL:

```javascript
const API_BASE_URL = "http://localhost:5000/api";
```

### Step 4: Test Frontend Integration

1. Open `mains/predict.html` in a browser
2. Select a species and adjust parameters
3. Click "Run Prediction"
4. Verify map updates with risk markers

### Step 5: Deploy to Production

For production deployment:

1. **Update API URL** in frontend files:
   ```javascript
   const API_BASE_URL = "https://your-domain.com/api";
   ```

2. **Deploy Flask API** using:
   - Gunicorn + Nginx
   - Docker container
   - Cloud platform (AWS, Azure, GCP)

3. **Enable HTTPS** for secure communication

4. **Set up CORS** for your production domain:
   ```python
   CORS(app, origins=["https://your-frontend-domain.com"])
   ```

## 📊 API Endpoints Summary

| Endpoint | Method | Purpose | Frontend Page |
|----------|--------|---------|---------------|
| `/api/health` | GET | Health check | All |
| `/api/species` | GET | Get species list | All (dropdown) |
| `/api/lakes` | GET | Get lakes list | - |
| `/api/lakes/<name>` | GET | Get lake info | - |
| `/api/predict` | POST | Get predictions | All |
| `/api/geojson` | POST | Get GeoJSON | predict.html |
| `/api/overview/most-contributing` | GET | Most important feature | Overview.html |
| `/api/interpretation/feature-importance` | GET | Feature analysis | interpretation.html |
| `/api/risk-scores` | POST | Risk scores table | risk_scores.html |

## 🔧 Configuration

### Backend Configuration

Edit `backend/backend.py` to customize:

```python
# Risk thresholds
def categorize_risk(score):
    if score < 0.34:  # Adjust this
        return "Low"
    elif score < 0.67:  # Adjust this
        return "Medium"
    else:
        return "High"

# Similarity decay rate
def calculate_similarity(user_env, lake_env):
    distance = np.linalg.norm(user_env - lake_env)
    return float(np.exp(-distance / 10))  # Adjust decay rate (10)
```

### Flask Configuration

Edit `backend/flask_api.py` to customize:

```python
# Port
app.run(debug=True, host='0.0.0.0', port=5000)

# CORS origins
CORS(app, origins=["http://localhost:3000"])

# Debug mode
app.run(debug=False)  # Set to False for production
```

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Solution: Add your frontend domain to CORS origins
   - Check browser console for specific error

2. **Model Not Found**
   - Solution: Verify model files exist in `model/` directory
   - Check file paths in `backend.py`

3. **Species Not Found**
   - Solution: Check species name matches exactly (case-sensitive)
   - Use `/api/species` to get valid species names

4. **Predictions All Zero**
   - Solution: Check if input parameters are valid
   - Verify preprocessor is working correctly

5. **Port Already in Use**
   - Solution: Change port in `flask_api.py`
   - Or kill existing process: `netstat -ano | findstr :5000`

## 📚 Additional Resources

- [Backend README](backend/README.md) - Detailed documentation
- [Quick Start Guide](backend/QUICKSTART.md) - Get started in 5 minutes
- [Test Suite](backend/test_backend.py) - Comprehensive tests

## ✅ Checklist

Before going live, verify:

- [ ] All tests pass (`python backend/test_backend.py`)
- [ ] Flask server starts without errors
- [ ] Frontend can connect to API
- [ ] Map displays risk markers correctly
- [ ] Risk scores table populates
- [ ] Feature importance chart displays
- [ ] Overview shows most contributing feature
- [ ] Species dropdown loads from API
- [ ] Error handling works (try invalid species)
- [ ] CORS is configured for production domain
- [ ] HTTPS is enabled for production

## 🎉 Success!

Your backend is now fully integrated with your frontend! Users can:

1. Select a species from the dropdown
2. Adjust environmental parameters with sliders
3. Click "Run Prediction"
4. See risk predictions on the map
5. View detailed risk scores in the table
6. Understand feature importance in the interpretation tab
7. See the most contributing feature in the overview

The system uses real machine learning predictions with environmental similarity weighting to provide accurate, context-aware invasion risk assessments!
