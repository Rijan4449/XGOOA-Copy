# 🔧 Troubleshooting Guide

## Issue 1: No Results When Clicking "Run Prediction"

### Symptoms
- Click "Run Prediction" button
- Loading spinner appears
- No markers appear on map
- No data in tables

### Solutions

#### Solution A: Backend Server Not Running
**Check if backend is running:**
1. Look for a terminal window with "Server running on http://localhost:5000"
2. If not running, start it:
   ```bash
   cd c:\Users\princ\XGOOA
   python backend/flask_api.py
   ```

#### Solution B: Species Not Selected
**Make sure you select a species:**
1. Click the "Species" dropdown
2. Select any species (e.g., "Climbing perch")
3. Then click "Run Prediction"

#### Solution C: Check Browser Console
**Open browser console (F12) and look for errors:**
1. Press F12 in your browser
2. Click "Console" tab
3. Look for red error messages
4. Common errors:
   - `Failed to fetch` → Backend not running
   - `Species not found` → Select a different species
   - `CORS error` → Backend CORS issue

#### Solution D: Test Backend Directly
**Test if backend is working:**
1. Open browser
2. Go to: `http://localhost:5000/api/health`
3. Should see: `{"status":"healthy",...}`
4. If you see this, backend is working!

### Quick Fix Steps
1. ✅ Start backend: `python backend/flask_api.py`
2. ✅ Select a species from dropdown
3. ✅ Set sliders to non-zero values (e.g., temp=27, pH=7.5)
4. ✅ Click "Run Prediction"
5. ✅ Wait for results (5-10 seconds)

---

## Issue 2: Values Reset to 0 When Changing Tabs

### Symptoms
- Set sliders to values (e.g., temp=27, pH=7.5)
- Click different tab (e.g., from Overview to Predict)
- All sliders reset to 0

### Why This Happens
Each HTML page is separate and doesn't remember values from other pages.

### Solution: Set Default Values
I've added a `shared_state.js` file that will remember your values, but you need to set them once per session.

### Workaround: Set Values on Each Page
**For now, set your values on each page:**
1. Open any page
2. Set sliders:
   - Temperature: 27°C
   - pH: 7.5
   - Salinity: 0.5
   - Dissolved Oxygen: 6.0
   - BOD: 2.0
   - Turbidity: 10.0
3. Select species
4. Click "Run Prediction"

### Recommended: Use One Page at a Time
**Best practice:**
1. Start with `Overview.html`
2. Set all values
3. Run prediction
4. View results
5. Then go to next page and set values again

---

## Issue 3: Backend Server Won't Start

### Symptoms
- Run `python backend/flask_api.py`
- Get error messages
- Server doesn't start

### Solutions

#### Solution A: Missing Dependencies
```bash
pip install pandas numpy xgboost joblib flask flask-cors
```

#### Solution B: Port 5000 Already in Use
**Error**: `Address already in use`

**Fix**: Change port in `backend/flask_api.py` (last line):
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001
```

Then update HTML files to use `http://localhost:5001/api`

#### Solution C: Model Files Missing
**Error**: `FileNotFoundError: mooa_xgb_model_v4.json`

**Fix**: Make sure these files exist:
- `model/mooa_xgb_model_v4.json`
- `model/mooa_preprocessor_v4.joblib`
- `dataset/super_dataset.csv`

---

## Issue 4: Species Dropdown is Empty

### Symptoms
- Open HTML page
- Species dropdown shows "Select a species" but no options

### Solutions

#### Solution A: CSV File Missing
**Check if file exists:**
```bash
dir assets\fish_description.csv
```

If missing, you need the CSV file with species data.

#### Solution B: CSV Format Wrong
**CSV must have these columns:**
- Species
- CommonName
- Description

#### Solution C: Check Browser Console
1. Press F12
2. Look for CSV loading errors
3. Check file path is correct

---

## Issue 5: Map Shows But No Markers

### Symptoms
- Map loads correctly
- Can zoom and pan
- But no colored markers appear

### Solutions

#### Solution A: No Prediction Run Yet
**You need to run a prediction first:**
1. Select species
2. Set parameters
3. Click "Run Prediction"
4. Wait for markers to appear

#### Solution B: Backend Returned Empty Data
**Check console (F12):**
- Look for "Received prediction data"
- Should show 13 lakes
- If empty, backend might have an error

#### Solution C: Species Not in Dataset
**Try a different species:**
- Some species might not be in the dataset
- Try "Anabas testudineus" (Climbing perch)
- This species is definitely in the dataset

---

## Issue 6: "Failed to Connect to Backend API"

### Symptoms
- Alert message: "Failed to connect to backend API"
- Or: "Make sure the backend server is running"

### Solutions

#### Solution A: Start Backend
```bash
cd c:\Users\princ\XGOOA
python backend/flask_api.py
```

#### Solution B: Check URL
**Make sure backend URL is correct in HTML:**
- Should be: `http://localhost:5000/api`
- Check in browser console what URL is being called

#### Solution C: Firewall Blocking
**Windows Firewall might be blocking:**
1. Allow Python through firewall
2. Or temporarily disable firewall for testing

---

## Quick Diagnostic Checklist

Run through this checklist:

- [ ] Backend server is running (terminal shows "Server running...")
- [ ] Can access `http://localhost:5000/api/health` in browser
- [ ] Species dropdown has options
- [ ] Selected a species
- [ ] Set sliders to non-zero values
- [ ] Clicked "Run Prediction"
- [ ] Waited at least 10 seconds
- [ ] Checked browser console (F12) for errors

---

## Common Error Messages

### "Please select a species first!"
**Fix**: Select a species from the dropdown before clicking "Run Prediction"

### "Species 'X' not found in dataset"
**Fix**: Try a different species. Use "Anabas testudineus" which is guaranteed to work.

### "Failed to fetch"
**Fix**: Backend server is not running. Start it with `python backend/flask_api.py`

### "CORS policy error"
**Fix**: Backend should have CORS enabled. Check `flask_api.py` has `CORS(app)`

### "HTTP error! status: 500"
**Fix**: Backend error. Check backend terminal for error messages.

---

## Testing Backend is Working

### Test 1: Health Check
```bash
curl http://localhost:5000/api/health
```
Should return: `{"status":"healthy",...}`

### Test 2: Get Species List
```bash
curl http://localhost:5000/api/species
```
Should return list of species

### Test 3: Make Prediction
Open browser console (F12) and run:
```javascript
fetch('http://localhost:5000/api/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    species: 'Anabas testudineus',
    temperature: 27,
    ph: 7.5,
    salinity: 0.5,
    dissolved_oxygen: 6,
    bod: 2,
    turbidity: 10
  })
}).then(r => r.json()).then(console.log)
```

Should return predictions for 13 lakes.

---

## Still Not Working?

### Step-by-Step Debug Process

1. **Verify Backend**:
   ```bash
   cd c:\Users\princ\XGOOA
   python backend/test_backend.py
   ```
   All 8 tests should pass.

2. **Start Backend**:
   ```bash
   python backend/flask_api.py
   ```
   Should see "Server running on http://localhost:5000"

3. **Test in Browser**:
   - Go to: `http://localhost:5000/api/health`
   - Should see JSON response

4. **Open HTML**:
   - Open `mains/predict.html`
   - Press F12 (open console)
   - Select species: "Anabas testudineus"
   - Set temp=27, pH=7.5, sal=0.5, DO=6, BOD=2, turb=10
   - Click "Run Prediction"
   - Watch console for messages

5. **Check Console Output**:
   - Should see: "Sending prediction request: {...}"
   - Should see: "Received prediction data: {...}"
   - If you see errors, read the error message

---

## Contact Information

If none of these solutions work:

1. Check backend terminal for error messages
2. Check browser console (F12) for JavaScript errors
3. Verify all files are in correct locations
4. Try restarting both backend and browser

---

**Most Common Fix**: Just make sure backend is running! 90% of issues are because the backend server isn't started.

```bash
cd c:\Users\princ\XGOOA
python backend/flask_api.py
```

Keep this terminal open while using the frontend!
