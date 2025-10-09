# Backend Quick Start Guide

Get up and running with the XGOOA Invasive Species Risk Prediction Backend in 5 minutes!

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## 🚀 Installation

### Step 1: Install Dependencies

Open a terminal and run:

```bash
pip install pandas numpy xgboost joblib flask flask-cors
```

### Step 2: Verify Installation

Navigate to the XGOOA directory:

```bash
cd c:\Users\princ\XGOOA
```

## ✅ Test the Backend

Run the comprehensive test suite:

```bash
python backend/test_backend.py
```

You should see output like:

```
======================================================================
  BACKEND TEST SUITE
======================================================================

--- Test 1: Get Species List ---
✓ Total species: 43
✓ First 5 species:
   1. Anabas testudineus
   2. Copella arnoldi
   ...

--- Test 2: Get Lake Information ---
✓ Lake: Laguna_de_Bay
✓ Region: CALABARZON
...

======================================================================
  TEST SUMMARY
======================================================================

Tests Passed: 8/8

🎉 All tests passed!
```

## 🌐 Start the API Server

Run the Flask API server:

```bash
python backend/flask_api.py
```

You should see:

```
======================================================================
INVASIVE SPECIES PREDICTION API SERVER
======================================================================

Available endpoints:
  GET  /api/health                              - Health check
  GET  /api/info                                - API information
  ...

======================================================================
Server running on http://localhost:5000
======================================================================
```

## 🧪 Test the API

### Using cURL

```bash
# Health check
curl http://localhost:5000/api/health

# Get species list
curl http://localhost:5000/api/species

# Predict invasion risk
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "species": "Anabas testudineus",
    "temperature": 27.0,
    "ph": 7.5,
    "salinity": 0.5,
    "dissolved_oxygen": 6.0,
    "bod": 2.0,
    "turbidity": 10.0
  }'
```

### Using Python

Create a file `test_api.py`:

```python
import requests
import json

# API base URL
BASE_URL = "http://localhost:5000/api"

# Test 1: Health check
response = requests.get(f"{BASE_URL}/health")
print("Health Check:", response.json())

# Test 2: Get species list
response = requests.get(f"{BASE_URL}/species")
data = response.json()
print(f"\nTotal Species: {data['count']}")

# Test 3: Predict invasion risk
payload = {
    "species": "Anabas testudineus",
    "temperature": 27.0,
    "ph": 7.5,
    "salinity": 0.5,
    "dissolved_oxygen": 6.0,
    "bod": 2.0,
    "turbidity": 10.0
}

response = requests.post(f"{BASE_URL}/predict", json=payload)
data = response.json()

if data['success']:
    print(f"\nTop 3 High-Risk Lakes:")
    for i, pred in enumerate(data['predictions'][:3], 1):
        print(f"{i}. {pred['lake_name']}: {pred['adjusted_score']:.3f} ({pred['risk_level']})")
```

Run it:

```bash
python test_api.py
```

## 🎨 Frontend Integration

### Update your HTML files

In `mains/predict.html`, update the API endpoint:

```javascript
// Change this line:
const EXTERNAL_GEOJSON_URL = "https://your-domain.example/luzon_invasion_points.geojson";

// To this:
const API_BASE_URL = "http://localhost:5000/api";

// Update the loadPoints function:
async function loadPoints({ useFormParams = false } = {}) {
    try {
        let url = `${API_BASE_URL}/geojson`;
        
        if (useFormParams) {
            const payload = {
                species: document.getElementById('specie').value,
                temperature: parseFloat(document.getElementById('temperature').value),
                ph: parseFloat(document.getElementById('water_ph').value),
                salinity: parseFloat(document.getElementById('salinity').value),
                dissolved_oxygen: parseFloat(document.getElementById('dissolved_oxygen').value),
                bod: parseFloat(document.getElementById('bod').value),
                turbidity: parseFloat(document.getElementById('turbidity').value)
            };
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            renderPoints(data);
        }
    } catch (err) {
        console.error("Failed to load predictions:", err);
    }
}
```

### Update All HTML Files

All HTML files have been updated with backend integration. The files are ready to use:

✅ **Overview.html** - Loads most contributing feature and displays prediction maps  
✅ **predict.html** - Shows interactive risk map with markers  
✅ **interpretation.html** - Displays feature importance analysis  
✅ **risk_scores.html** - Shows risk scores table with all lakes  

**No additional updates needed!** Just start the backend server and open any HTML file in your browser.

## 📊 Using the Backend Directly in Python

You can also use the backend module directly in Python scripts:

```python
from backend import backend

# Get risk predictions
result = backend.get_risk_predictions(
    species_name="Anabas testudineus",
    temperature=27.0,
    ph=7.5,
    salinity=0.5,
    do=6.0,
    bod=2.0,
    turbidity=10.0
)

# Print results
for pred in result['predictions']:
    print(f"{pred['lake_name']}: {pred['adjusted_score']:.3f} ({pred['risk_level']})")

# Get most contributing feature
feature = backend.get_most_contributing_feature()
print(f"\nMost Contributing Feature: {feature['most_contributing_feature']}")

# Get feature importance analysis
analysis = backend.get_feature_importance_analysis()
for param in analysis['aggregated_importance']:
    print(f"{param['parameter']}: {param['percentage']:.1f}%")
```

## 🔧 Troubleshooting

### Issue: "Module not found"

**Solution**: Make sure you're in the correct directory:

```bash
cd c:\Users\princ\XGOOA
python backend/test_backend.py
```

### Issue: "Port 5000 already in use"

**Solution**: Change the port in `flask_api.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use port 5001 instead
```

### Issue: "Model file not found"

**Solution**: Verify the model files exist:

```bash
dir model\mooa_xgb_model_v4.json
dir model\mooa_preprocessor_v4.joblib
```

### Issue: CORS errors in browser

**Solution**: The Flask server already has CORS enabled. If you still see errors, try:

1. Use the same origin (serve frontend from Flask)
2. Or add specific origins in `flask_api.py`:

```python
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:5500"])
```

## 📚 Next Steps

1. ✅ Read the full [README.md](README.md) for detailed documentation
2. ✅ Explore the API endpoints using the `/api/info` endpoint
3. ✅ Integrate with your frontend HTML files
4. ✅ Customize risk thresholds if needed
5. ✅ Add more lakes or species to the dataset

## 🆘 Need Help?

- Check the [README.md](README.md) for detailed documentation
- Run `python backend/test_backend.py` to verify everything works
- Check the Flask server logs for error messages
- Verify all dependencies are installed: `pip list`

## 🎉 Success!

If all tests pass and the API server starts successfully, you're ready to use the backend!

Try opening your frontend in a browser and making predictions. The map should now display real risk predictions from the backend!
