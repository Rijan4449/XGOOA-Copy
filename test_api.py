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
