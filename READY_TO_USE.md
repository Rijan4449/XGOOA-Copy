# 🚀 READY TO USE - Quick Start

Your XGOOA system is **100% ready to use**! Follow these 2 simple steps:

## Step 1: Start Backend Server (1 command)

Open a terminal and run:

```bash
cd c:\Users\princ\XGOOA
python backend/flask_api.py
```

You should see:
```
======================================================================
Server running on http://localhost:5000
======================================================================
```

**Keep this terminal window open!**

## Step 2: Open Frontend in Browser

Simply open any of these HTML files in your browser:

### Option A: Double-click to open
- `mains/Overview.html` ← Start here!
- `mains/predict.html`
- `mains/interpretation.html`
- `mains/risk_scores.html`

### Option B: Right-click → Open with → Your Browser

## 🎯 How to Use

1. **Select a species** from the dropdown
2. **Adjust parameters** using the sliders:
   - Temperature (°C)
   - Water pH
   - Salinity (ppt)
   - Dissolved Oxygen (mg/L)
   - BOD (mg/L)
   - Turbidity (NTU)
3. **Click "Run Prediction"**
4. **View results**:
   - Overview: See most contributing feature + prediction maps
   - Predict: Interactive risk map with markers
   - Interpretation: Feature importance analysis
   - Risk Scores: Table with all 13 lakes

## ✅ What Each Page Shows

### 📊 Overview.html
- **Most Contributing Feature**: Shows which parameter (pH, BOD, Temperature, etc.) is most important
- **Highest Probability Map**: Top 5 lakes with highest invasion risk
- **Presence Occurrence Map**: Lakes where species is confirmed present

### 🗺️ predict.html
- **Interactive Map**: All 13 Luzon lakes with risk markers
- **Color-coded**: 
  - 🔴 Red = High Risk (≥67%)
  - 🟡 Yellow = Medium Risk (34-67%)
  - 🟢 Green = Low Risk (<34%)
- **Popups**: Click markers to see details

### 📈 interpretation.html
- **Feature Importance Table**: Shows which environmental parameters matter most
- **Progress Bars**: Visual representation of importance
- **Percentages**: Exact contribution of each parameter

### 📋 risk_scores.html
- **Complete Table**: All 13 lakes with:
  - Lake name
  - Region
  - Invasion Risk Score (0-1)
  - Risk Level (Low/Medium/High)
  - Species Presence (Yes/No/Unknown)
- **Sortable**: Click column headers to sort

## 🎨 Risk Level Guide

The system categorizes risk into 3 levels:

| Risk Level | Score Range | Color | Meaning |
|------------|-------------|-------|---------|
| 🟢 Low | 0.00 - 0.33 | Green | Low probability of invasion |
| 🟡 Medium | 0.34 - 0.66 | Yellow | Moderate invasion risk |
| 🔴 High | 0.67 - 1.00 | Red | High probability of invasion |

## 📍 The 13 Luzon Lakes

Your system predicts risk for these lakes:

**CALABARZON Region (10 lakes)**:
1. Laguna de Bay
2. Lake Taal
3. Sampaloc Lake
4. Yambo Lake
5. Pandin Lake
6. Mohicap Lake
7. Palakpakin Lake
8. Nabao Lake
9. Tadlac Lake
10. Bunot Lake

**Bicol Region (1 lake)**:
11. Lake Buhi

**Leyte Region (1 lake)**:
12. Lake Danao

**CALABARZON Region (1 lake)**:
13. Tikub Lake

## 🔧 Troubleshooting

### Problem: "Failed to connect to backend API"
**Solution**: Make sure the backend server is running (Step 1)

### Problem: Dropdown is empty
**Solution**: Check that `assets/fish_description.csv` exists

### Problem: No predictions showing
**Solution**: 
1. Select a species first
2. Make sure all sliders have values (not 0)
3. Click "Run Prediction"

### Problem: Port 5000 already in use
**Solution**: 
1. Close other programs using port 5000
2. Or change port in `backend/flask_api.py` (line 200):
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```
   Then update HTML files to use `http://localhost:5001/api`

## 📝 Example Usage

### Predict Risk for Climbing Perch (Anabas testudineus)

1. Open `mains/Overview.html`
2. Select "Climbing perch (Anabas testudineus)" from dropdown
3. Set parameters:
   - Temperature: 27.0°C
   - pH: 7.5
   - Salinity: 0.5 ppt
   - Dissolved Oxygen: 6.0 mg/L
   - BOD: 2.0 mg/L
   - Turbidity: 10.0 NTU
4. Click "Run Prediction"
5. View results:
   - Most Contributing Feature: BOD (23.4%)
   - Highest risk lakes appear on map
   - Presence locations shown on second map

### View Feature Importance

1. Open `mains/interpretation.html`
2. Page automatically loads feature importance
3. See which parameters matter most:
   - BOD: 23.4%
   - Temperature: 20.7%
   - pH: 16.7%
   - Dissolved Oxygen: 13.9%
   - Turbidity: 11.6%
   - Salinity: 10.0%

### Check Risk Scores for All Lakes

1. Open `mains/risk_scores.html`
2. Select species and set parameters
3. Click "Run Prediction"
4. Table shows all 13 lakes sorted by risk
5. See which lakes have highest invasion risk

## 🎉 You're All Set!

Everything is configured and ready to use. Just:
1. Start the backend server
2. Open any HTML file
3. Make predictions!

**No additional setup required!** 🚀

---

## 📚 Additional Resources

- **Detailed Documentation**: See `backend/README.md`
- **Quick Start Guide**: See `backend/QUICKSTART.md`
- **Integration Guide**: See `BACKEND_INTEGRATION_GUIDE.md`
- **System Architecture**: See `SYSTEM_ARCHITECTURE.md`

## 💡 Tips

- **Keep backend running**: Don't close the terminal with the backend server
- **Refresh browser**: If something doesn't work, try refreshing the page
- **Check console**: Press F12 in browser to see any error messages
- **Try different species**: The system has 40+ species to choose from
- **Experiment with parameters**: See how different values affect predictions

## 🆘 Still Need Help?

1. Check if backend server is running (terminal should show "Server running...")
2. Check browser console (F12) for error messages
3. Verify files exist:
   - `model/mooa_xgb_model_v4.json`
   - `model/mooa_preprocessor_v4.joblib`
   - `dataset/super_dataset.csv`
   - `assets/fish_description.csv`

---

**Happy Predicting! 🐟🗺️📊**

*XGOOA - Invasive Species Risk Prediction System*  
*Version 2.0 - Ready to Use*
