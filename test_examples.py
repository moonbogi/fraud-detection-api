"""
Manual testing script for the fraud detection API.
Start the server (python main.py) then run this to test different scenarios.
"""

import requests
import json
from typing import Dict, Any

API_BASE = "http://localhost:8000"


def print_response(title: str, response: Dict[Any, Any]):
def print_response(title: str, response: Dict[Any, Any]):
    """Print the response nicely."""
    print(f"{title}")
    print('='*60)
    print(json.dumps(response, indent=2))


def test_health():
    """Check if server is running."""
    response = requests.get(f"{API_BASE}/health")
    print_response("Health Check", response.json())


def test_low_risk_transaction():
    """Test a normal, low-risk transaction."""
    transaction = {
        "transaction_id": "txn_low_001",
        "amount": 47.32,
        "merchant": "Starbucks",
        "category": "food",
        "location": "San Francisco, CA",
        "timestamp": "2024-12-08T08:15:00Z",
        "card_last_four": "5678"
    }
    
    response = requests.post(f"{API_BASE}/analyze", json=transaction)
    print_response("Low Risk Transaction - Starbucks Purchase", response.json())


def test_medium_risk_transaction():
    """Test a moderately suspicious transaction."""
    transaction = {
        "transaction_id": "txn_med_001",
        "amount": 1500.00,
        "merchant": "Online Electronics",
        "category": "electronics",
        "location": "International",
        "timestamp": "2024-12-08T23:45:00Z",
        "card_last_four": "1234"
    }
    
    response = requests.post(f"{API_BASE}/analyze", json=transaction)
    print_response("Medium Risk Transaction - Late Night International Purchase", response.json())


def test_high_risk_transaction():
    """Test a highly suspicious transaction."""
    transaction = {
        "transaction_id": "txn_high_001",
        "amount": 10000.00,
        "merchant": "Wire Transfer Service",
        "category": "financial",
        "location": "Nigeria",
        "timestamp": "2024-12-08T03:00:00Z",
        "card_last_four": "9012"
    }
    
    response = requests.post(f"{API_BASE}/analyze", json=transaction)
    print_response("High Risk Transaction - Large Wire Transfer", response.json())


def test_round_amount_suspicious():
    """Test transaction with suspicious round amount."""
    transaction = {
        "transaction_id": "txn_round_001",
        "amount": 5000.00,
        "merchant": "Gift Cards Plus",
        "category": "retail",
        "location": "Unknown",
        "timestamp": "2024-12-08T02:30:00Z",
        "card_last_four": "3456"
    }
    
    response = requests.post(f"{API_BASE}/analyze", json=transaction)
    print_response("Suspicious Round Amount - Gift Card Purchase", response.json())


def test_validation_error():
    """Test validation with invalid card number."""
    transaction = {
        "transaction_id": "txn_invalid_001",
        "amount": 50.00,
        "merchant": "Test Merchant",
        "category": "retail",
        "location": "Test City",
        "timestamp": "2024-12-08T12:00:00Z",
        "card_last_four": "12345678"  # Invalid: too many digits
    }
    
    try:
        response = requests.post(f"{API_BASE}/analyze", json=transaction)
        print_response("Validation Error Test", response.json())
    except Exception as e:
        print(f"\n{'='*60}")
        print("Validation Error Test (Expected)")
        print('='*60)
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\nStarting Fraud Detection API Tests")
    print("Make sure the server is running: python main.py\n")
    
    try:
        # Test health first
        test_health()
        
        # Test various scenarios
        test_low_risk_transaction()
        test_medium_risk_transaction()
        test_high_risk_transaction()
        test_round_amount_suspicious()
        test_validation_error()
        
        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API")
        print("Make sure the server is running: python main.py\n")
    except Exception as e:
        print(f"\nUnexpected error: {e}\n")
