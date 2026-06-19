def calculate_investment_score(airport_data: dict) -> float:
    """
    Calculates a deterministic investment score for a given airport.
    
    Factors might include:
    - Current flight volume
    - Delay index (indicating congestion)
    - Unmet demand estimate
    """
    # TODO: Implement the real deterministic logic based on chosen API
    # This is a stub implementation.
    
    base_score = airport_data.get("mock_flight_volume", 0) * 0.01
    congestion_multiplier = airport_data.get("mock_delay_index", 1.0)
    
    final_score = base_score * congestion_multiplier
    
    return final_score

def rank_airports(airports_data: list) -> list:
    """
    Ranks a list of airports based on their investment score.
    """
    scored_airports = []
    for data in airports_data:
        score = calculate_investment_score(data)
        scored_airports.append({
            "airport": data.get("airport"),
            "score": score
        })
        
    # Sort descending by score
    scored_airports.sort(key=lambda x: x["score"], reverse=True)
    return scored_airports
