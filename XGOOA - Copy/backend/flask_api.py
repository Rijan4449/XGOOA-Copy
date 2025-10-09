"""
Flask API Server for Invasive Species Risk Prediction
======================================================
REST API endpoints for the frontend to call.
Integrates with the comprehensive backend.py module.

Author: XGOOA Team
Version: 2.0
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os

# Add parent directory to path to import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import backend

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "Invasive Species Prediction API is running",
        "version": "2.0"
    })


@app.route('/api/info', methods=['GET'])
def get_info():
    """Get API information and available endpoints."""
    return jsonify({
        "api_name": "Invasive Species Risk Prediction API",
        "version": "2.0",
        "endpoints": {
            "GET /api/health": "Health check",
            "GET /api/info": "API information",
            "GET /api/species": "Get all species",
            "GET /api/lakes": "Get all lakes",
            "GET /api/lakes/<name>": "Get specific lake info",
            "POST /api/predict": "Predict invasion risk for all lakes",
            "GET /api/overview/most-contributing": "Get most contributing feature",
            "GET /api/interpretation/feature-importance": "Get feature importance analysis",
            "POST /api/geojson": "Get predictions as GeoJSON for map"
        }
    })


# ============================================================================
# SPECIES ENDPOINTS
# ============================================================================

@app.route('/api/species', methods=['GET'])
def get_species_list():
    """Get list of all available species."""
    try:
        species_list = backend.get_species_list()
        return jsonify({
            "success": True,
            "count": len(species_list),
            "species": species_list
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# LAKE ENDPOINTS
# ============================================================================

@app.route('/api/lakes', methods=['GET'])
def get_lakes():
    """Get list of all Luzon lakes."""
    try:
        lakes = []
        for _, lake in backend.luzon_lakes.iterrows():
            lakes.append({
                "name": lake["Lake Name"],
                "region": lake["Region"],
                "latitude": float(lake["Latitude"]),
                "longitude": float(lake["Longitude"])
            })
        
        return jsonify({
            "success": True,
            "count": len(lakes),
            "lakes": lakes
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/lakes/<lake_name>', methods=['GET'])
def get_lake_info(lake_name):
    """Get detailed information about a specific lake."""
    try:
        lake_info = backend.get_lake_info(lake_name)
        
        if lake_info is None:
            return jsonify({
                "success": False,
                "error": f"Lake '{lake_name}' not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": lake_info
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================

@app.route('/api/predict', methods=['POST'])
def predict_invasion():
    """
    Predict invasion risk for all Luzon lakes.
    
    Expected JSON body:
    {
        "species": "Anabas testudineus",
        "temperature": 27.0,
        "ph": 7.5,
        "salinity": 0.5,
        "dissolved_oxygen": 6.0,
        "bod": 2.0,
        "turbidity": 10.0
    }
    
    Returns:
    {
        "success": true,
        "predictions": [...],
        "warning": "..." (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['species', 'temperature', 'ph', 'salinity', 
                          'dissolved_oxygen', 'bod', 'turbidity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Call backend function
        result = backend.get_risk_predictions(
            species_name=data['species'],
            temperature=float(data['temperature']),
            ph=float(data['ph']),
            salinity=float(data['salinity']),
            do=float(data['dissolved_oxygen']),
            bod=float(data['bod']),
            turbidity=float(data['turbidity'])
        )
        
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400
        
        return jsonify({
            "success": True,
            **result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/geojson', methods=['POST'])
def get_geojson():
    """
    Get predictions as GeoJSON for map visualization.
    
    Expected JSON body: Same as /api/predict
    
    Returns GeoJSON FeatureCollection with lake points and risk data.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['species', 'temperature', 'ph', 'salinity', 
                          'dissolved_oxygen', 'bod', 'turbidity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Get predictions
        result = backend.get_risk_predictions(
            species_name=data['species'],
            temperature=float(data['temperature']),
            ph=float(data['ph']),
            salinity=float(data['salinity']),
            do=float(data['dissolved_oxygen']),
            bod=float(data['bod']),
            turbidity=float(data['turbidity'])
        )
        
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400
        
        # Convert to GeoJSON
        features = []
        for pred in result["predictions"]:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [pred["longitude"], pred["latitude"]]
                },
                "properties": {
                    "name": pred["lake_name"],
                    "region": pred["region"],
                    "prob": pred["adjusted_score"],
                    "percentage": pred["adjusted_score"] * 100,
                    "risk_category": pred["risk_level"],
                    "raw_score": pred["raw_score"],
                    "similarity": pred["similarity"],
                    "presence": pred["presence"],
                    "species": data['species']
                }
            }
            features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        if "warning" in result:
            geojson["warning"] = result["warning"]
        
        return jsonify(geojson)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# OVERVIEW ENDPOINTS
# ============================================================================

@app.route('/api/overview/most-contributing', methods=['GET'])
def get_most_contributing():
    """Get the most contributing environmental feature."""
    try:
        result = backend.get_most_contributing_feature()
        
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# INTERPRETATION ENDPOINTS
# ============================================================================

@app.route('/api/interpretation/feature-importance', methods=['GET'])
def get_feature_importance():
    """Get detailed feature importance analysis."""
    try:
        result = backend.get_feature_importance_analysis()
        
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 500
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# RISK SCORES ENDPOINTS
# ============================================================================

@app.route('/api/risk-scores', methods=['POST'])
def get_risk_scores():
    """
    Get risk scores table data.
    
    Expected JSON body:
    {
        "species": "Anabas testudineus",
        "temperature": 27.0,
        "ph": 7.5,
        "salinity": 0.5,
        "dissolved_oxygen": 6.0,
        "bod": 2.0,
        "turbidity": 10.0
    }
    
    Returns table data for the Risk Scores tab.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['species', 'temperature', 'ph', 'salinity', 
                          'dissolved_oxygen', 'bod', 'turbidity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Get predictions
        result = backend.get_risk_predictions(
            species_name=data['species'],
            temperature=float(data['temperature']),
            ph=float(data['ph']),
            salinity=float(data['salinity']),
            do=float(data['dissolved_oxygen']),
            bod=float(data['bod']),
            turbidity=float(data['turbidity'])
        )
        
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400
        
        # Format for table
        table_data = []
        for pred in result["predictions"]:
            table_data.append({
                "lake": pred["lake_name"],
                "region": pred["region"],
                "score": pred["adjusted_score"],
                "risk_level": pred["risk_level"],
                "presence": pred["presence"]
            })
        
        return jsonify({
            "success": True,
            "count": len(table_data),
            "data": table_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("INVASIVE SPECIES PREDICTION API SERVER")
    print("=" * 70)
    print("\nAvailable endpoints:")
    print("  GET  /api/health                              - Health check")
    print("  GET  /api/info                                - API information")
    print("  GET  /api/species                             - Get all species")
    print("  GET  /api/lakes                               - Get all lakes")
    print("  GET  /api/lakes/<name>                        - Get lake info")
    print("  POST /api/predict                             - Predict risk for all lakes")
    print("  POST /api/geojson                             - Get predictions as GeoJSON")
    print("  GET  /api/overview/most-contributing          - Most contributing feature")
    print("  GET  /api/interpretation/feature-importance   - Feature importance analysis")
    print("  POST /api/risk-scores                         - Risk scores table")
    print("\n" + "=" * 70)
    print("Server running on http://localhost:5000")
    print("=" * 70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
