"""
XGOOA Backend Package
=====================
Invasive Species Risk Prediction Backend Module

This package provides comprehensive backend functionality for predicting
invasion risk of species across Luzon lakes.

Main Functions:
- get_risk_predictions(): Predict risk for all lakes
- get_most_contributing_feature(): Get most important parameter
- get_feature_importance_analysis(): Get detailed feature analysis

Usage:
    from backend import backend
    
    result = backend.get_risk_predictions(
        species_name="Anabas testudineus",
        temperature=27.0,
        ph=7.5,
        salinity=0.5,
        do=6.0,
        bod=2.0,
        turbidity=10.0
    )
"""

__version__ = "2.0"
__author__ = "XGOOA Team"

# Import main functions for easy access
from .backend import (
    get_risk_predictions,
    get_most_contributing_feature,
    get_feature_importance_analysis,
    get_species_list,
    get_lake_info,
    categorize_risk,
    calculate_similarity
)

__all__ = [
    'get_risk_predictions',
    'get_most_contributing_feature',
    'get_feature_importance_analysis',
    'get_species_list',
    'get_lake_info',
    'categorize_risk',
    'calculate_similarity'
]
