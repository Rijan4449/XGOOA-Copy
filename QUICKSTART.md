# Quick Start Guide - Invasive Species Risk Prediction Backend

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Test the Backend

```bash
python test_backend.py
```

You should see all tests pass ✓

### Step 3: Start the API Server

```bash
python flask_server.py
```

Server will start on `http://localhost:5000`

### Step 4: Test the API

Open a new terminal and test with curl:

```bash
# Health check
curl http://localhost:5000/api/health

# Get species list
curl http://localhost:5000/api/species

# Make a prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "species": "Anabas testudineus",
    "temperature": 27.0,
    "ph": 7.5,
    "salinity": 0.0,
    "dissolved_oxygen": 6.0,
    "bod": 2.0,
    "turbidity": 10.0
  }'
```

### Step 5: Integrate with Frontend

Update `mains/predict.html`:

```javascript
// Change this line (around line 40):
const EXTERNAL_GEOJSON_URL = "http://localhost:5000/api/predict/luzon-lakes";

// Update loadPoints function to use POST:
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
    renderPoints(FALLBACK_FEATURES);
  }
}
```

### Step 6: Open the Frontend

Open `mains/predict.html` in your browser. The map should now show real predictions!

## 📝 Quick Examples

### Python Usage

```python
from backend_api import InvasiveSpeciesPredictor

# Initialize
predictor = InvasiveSpeciesPredictor()

# Get species list
species = predictor.get_species_list()
print(f"Available species: {len(species)}")

# Make prediction
result = predictor.predict_single(
    species="Anabas testudineus",
    temperature=27.0,
    ph=7.5,
    salinity=0.0,
    dissolved_oxygen=6.0,
    bod=2.0,
    turbidity=10.0
)

print(f"Risk: {result['invasion_percentage']:.1f}%")
print(f"Category: {result['risk_category']}")

# Generate map data
geojson = predictor.predict_for_luzon_lakes(
    species="Anabas testudineus",
    temperature=27.0,
    ph=7.5
)

# Save to file
import json
with open('luzon_predictions.geojson', 'w') as f:
    json.dump(geojson, f, indent=2)
```

### JavaScript (Frontend)

```javascript
// Fetch prediction
async function getPrediction() {
  const response = await fetch('http://localhost:5000/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      species: "Anabas testudineus",
      temperature: 27.0,
      ph: 7.5,
      salinity: 0.0,
      dissolved_oxygen: 6.0,
      bod: 2.0,
      turbidity: 10.0
    })
  });
  
  const result = await response.json();
  console.log(`Risk: ${result.invasion_percentage}%`);
}

// Fetch Luzon lakes GeoJSON
async function getLuzonMap() {
  const response = await fetch('http://localhost:5000/api/predict/luzon-lakes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      species: "Anabas testudineus",
      temperature: 27.0,
      ph: 7.5,
      salinity: 0.0,
      dissolved_oxygen: 6.0,
      bod: 2.0,
      turbidity: 10.0
    })
  });
  
  const geojson = await response.json();
  // Use with Leaflet map
  L.geoJSON(geojson).addTo(map);
}
```

## 🔧 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "Model file not found" error
Verify these files exist:
- `model/mooa_xgb_model_v4.json`
- `model/mooa_preprocessor_v4.joblib`
- `dataset/super_dataset.csv`

### CORS error in browser
Make sure Flask server is running and flask-cors is installed:
```bash
pip install flask-cors
```

### Port already in use
Change port in `flask_server.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001 instead
```

## ��� Next Steps

1. ✅ Read `BACKEND_README.md` for detailed documentation
2. ✅ Explore API endpoints with Postman or curl
3. ✅ Customize frontend integration
4. ✅ Add SHAP interpretation (optional)
5. ✅ Deploy to production server

## 🎯 Key Files

| File | Purpose |
|------|---------|
| `backend_api.py` | Core prediction module |
| `flask_server.py` | REST API server |
| `test_backend.py` | Test suite |
| `requirements.txt` | Python dependencies |
| `BACKEND_README.md` | Full documentation |

## 💡 Tips

- Use `test_backend.py` to verify everything works
- Check console output for debugging
- API returns JSON - easy to integrate with any frontend
- GeoJSON format works directly with Leaflet maps
- Risk categories are color-coded for visualization

## 🆘 Need Help?

1. Run `python test_backend.py` to diagnose issues
2. Check error messages in console
3. Verify all dependencies are installed
4. Ensure model files are present
5. Review `BACKEND_README.md` for details

---

**Ready to predict invasive species risk! 🐟🗺️**
