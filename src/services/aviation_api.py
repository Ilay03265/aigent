import os
import requests

def get_airport_data(airport_code: str):
    """
    Fetches aviation data for a given airport code.
    This is a stub function to be implemented once the API provider is chosen.
    """
    # TODO: Implement API fetching logic
    # Example:
    # api_key = os.getenv("AVIATION_API_KEY")
    # response = requests.get(f"API_URL?access_key={api_key}&query={airport_code}")
    # return response.json()
    
    return {
        "airport": airport_code,
        "mock_flight_volume": 1000,
        "mock_delay_index": 1.5,
        "mock_long_haul_percentage": 25.0
    }
