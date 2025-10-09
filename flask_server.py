"""
Flask API Server for Invasive Species Risk Prediction
======================================================
REST API endpoints for the frontend to call.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from backend_api import InvasiveSpeciesPredictor

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize predictor (singleton)
predictor = None

def get_predictor():
    """Get or create predictor instance."""
    global predictor
    if predictor is None:
        predictor = InvasiveSpeciesPredictor()
    return predictor


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "Invasive Species Prediction API is running"
    })


@app.route('/api/species', methods=['GET'])
def get_species_list():
    """Get list of all available species."""
    try:
        pred = get_predictor()
        species_list = pred.get_species_list()
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


@app.route('/api/species/<species_name>', methods=['GET'])
def get_species_info(species_name):
    """Get detailed information about a specific species."""
    try:
        pred = get_predictor()
        info = pred.get_species_info(species_name)
        return jsonify({
            "success": True,
            "data": info
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/predict', methods=['POST'])
def predict_invasion():
    """
    Predict invasion risk for a single species.
    
    Expected JSON body:
    {
        "species": "Anabas testudineus",
        "temperature": 27.0,
        "ph": 7.5,
        "salinity": 0.0,
        "dissolved_oxygen": 6.0,
        "bod": 2.0,
        "turbidity": 10.0
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
        
        pred = get_predictor()
        result = pred.predict_single(
            species=data['species'],
            temperature=float(data['temperature']),
            ph=float(data['ph']),
            salinity=float(data['salinity']),
            dissolved_oxygen=float(data['dissolved_oxygen']),
            bod=float(data['bod']),
            turbidity=float(data['turbidity'])
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/predict/luzon-lakes', methods=['POST'])
def predict_luzon_lakes():
    """
    Generate predictions for Luzon lakes (GeoJSON format).
    
    Expected JSON body:
    {
        "species": "Anabas testudineus",
        "temperature": 27.0,
        "ph": 7.5,
        "salinity": 0.0,
        "dissolved_oxygen": 6.0,
        "bod": 2.0,
        "turbidity": 10.0
    }
    """
    try:
        data = request.get_json()
        
        pred = get_predictor()
        geojson = pred.predict_for_luzon_lakes(
            species=data.get('species', 'Anabas testudineus'),
            temperature=float(data.get('temperature', 27.0)),
            ph=float(data.get('ph', 7.5)),
            salinity=float(data.get('salinity', 0.0)),
            dissolved_oxygen=float(data.get('dissolved_oxygen', 6.0)),
            bod=float(data.get('bod', 2.0)),
            turbidity=float(data.get('turbidity', 10.0))
        )
        
        return jsonify(geojson)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/risk-scores', methods=['POST'])
def get_risk_scores():
    """
    Get risk scores table for multiple species.
    
    Expected JSON body:
    {
        "temperature": 27.0,
        "ph": 7.5,
        "salinity": 0.0,
        "dissolved_oxygen": 6.0,
        "bod": 2.0,
        "turbidity": 10.0,
        "top_n": 20
    }
    """
    try:
        data = request.get_json() or {}
        
        pred = get_predictor()
        df = pred.get_risk_scores_table(
            temperature=float(data.get('temperature', 27.0)),
            ph=float(data.get('ph', 7.5)),
            salinity=float(data.get('salinity', 0.0)),
            dissolved_oxygen=float(data.get('dissolved_oxygen', 6.0)),
            bod=float(data.get('bod', 2.0)),
            turbidity=float(data.get('turbidity', 10.0)),
            top_n=int(data.get('top_n', 20))
        )
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')
        
        return jsonify({
            "success": True,
            "count": len(records),
            "data": records
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/overview', methods=['GET'])
def get_overview():
    """Get overview statistics."""
    try:
        pred = get_predictor()
        
        stats = {
            "total_species": len(pred.species_list),
            "total_records": len(pred.dataset),
            "model_type": "XGBoost Classifier",
            "model_version": "v4"
        }
        
        # Status distribution
        if 'status' in pred.dataset.columns:
            status_counts = pred.dataset['status'].value_counts().to_dict()
            stats["status_distribution"] = status_counts
        
        # Risk distribution
        if 'invasion_risk_score' in pred.dataset.columns:
            stats["risk_distribution"] = {
                "high_risk": int(len(pred.dataset[pred.dataset['invasion_risk_score'] >= 0.7])),
                "moderate_risk": int(len(pred.dataset[(pred.dataset['invasion_risk_score'] >= 0.3) & 
                                                      (pred.dataset['invasion_risk_score'] < 0.7)])),
                "low_risk": int(len(pred.dataset[pred.dataset['invasion_risk_score'] < 0.3]))
            }
        
        return jsonify({
            "success": True,
            "data": stats
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


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


if __name__ == '__main__':
    print("=" * 60)
    print("Starting Invasive Species Prediction API Server")
    print("=" * 60)
    print("\nAvailable endpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/species             - Get all species")
    print("  GET  /api/species/<name>      - Get species info")
    print("  POST /api/predict             - Single prediction")
    print("  POST /api/predict/luzon-lakes - Luzon lakes GeoJSON")
    print("  POST /api/risk-scores         - Risk scores table")
    print("  GET  /api/overview            - Overview statistics")
    print("\n" + "=" * 60)
    print("Server running on http://localhost:5000")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
