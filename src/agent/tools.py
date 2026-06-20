import math
from rich.console import Console
import os
import requests
import json
from agents import function_tool
import airportsdata
from .websearchAgent import planner_agent

tool1 = planner_agent.as_tool(tool_name="websearch_agent", tool_description="websearch for answers for questions with Airport topic , that needs a deep research in the web to answer it correctly")

console = Console()

AEROAPI_KEY = os.environ.get("AEROAPI_KEY")
AEROAPI_BASE_URL = "https://aeroapi.flightaware.com/aeroapi"

# Load airport databases for resolution
airports_icao = airportsdata.load('icao')
airports_iata = airportsdata.load('iata')

def _resolve_icao(airport_code: str) -> str:
    """Helper to convert any airport code/name into a standard ICAO code."""
    code = airport_code.upper().strip()
    if code in airports_icao:
        return code
    if code in airports_iata:
        return airports_iata[code]['icao']
    for icao, data in airports_icao.items():
        if code in data['name'].upper():
            return icao
    return code # Fallback to whatever they typed if we can't find it

def _fetch_all_pages(url: str, list_key: str) -> list[dict]:
    """Helper to fetch all pages for a given AeroAPI endpoint."""
    if not AEROAPI_KEY:
        return []
    
    headers = {"x-apikey": AEROAPI_KEY}
    all_items = []
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            all_items.extend(data.get(list_key, []))
            
            cursor = data.get("links", {}).get("next")
            pages_fetched = 1
            while cursor and pages_fetched < 40: # Pull up to 40 pages max
                next_url = f"{AEROAPI_BASE_URL}{cursor}"
                next_resp = requests.get(next_url, headers=headers, timeout=15)
                if next_resp.status_code == 200:
                    next_data = next_resp.json()
                    all_items.extend(next_data.get(list_key, []))
                    cursor = next_data.get("links", {}).get("next")
                    pages_fetched += 1
                else:
                    break
    except Exception as e:
        console.print(f"Error fetching data: {e}")
    
    return all_items

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance in kilometers between two points on the earth."""
    R = 6371.0 # Radius of earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

@function_tool
def get_airport_flights(airport_code: str) -> str:
    """
    Fetches the total real number of scheduled arrivals and departures for a given airport using FlightAware AeroAPI.
    
    Args:
        airport_code: The ICAO or IATA code or name of the airport (e.g., KLAX, JFK, LHR).
    """
    icao = _resolve_icao(airport_code)
    
    arr_url = f"{AEROAPI_BASE_URL}/airports/{icao}/flights/scheduled_arrivals"
    dep_url = f"{AEROAPI_BASE_URL}/airports/{icao}/flights/scheduled_departures"
    
    arrivals = _fetch_all_pages(arr_url, "scheduled_arrivals")
    departures = _fetch_all_pages(dep_url, "scheduled_departures")
    
    total_flights = len(arrivals) + len(departures)
    
    return f"The total number of scheduled flights (arrivals and departures) at {icao} is {total_flights}. (Based on {len(arrivals)} arrivals and {len(departures)} departures)."

@function_tool
def get_congestion_level(airport_code: str) -> str:
    """
    Calculates the congestion level of an airport by dividing the number of delayed scheduled departures by the total scheduled departures.
    
    Args:
        airport_code: The ICAO or IATA code or name of the airport.
    """
    icao = _resolve_icao(airport_code)
    dep_url = f"{AEROAPI_BASE_URL}/airports/{icao}/flights/scheduled_departures"
    departures = _fetch_all_pages(dep_url, "scheduled_departures")
    
    total_scheduled = len(departures)
    if total_scheduled == 0:
        return json.dumps({"congestion_ratio": 0.0, "delayed_count": 0, "total_scheduled": 0})
        
    delayed_count = sum(1 for flight in departures if flight.get("departure_delay", 0) > 0)
    congestion_ratio = delayed_count / total_scheduled
    
    return json.dumps({"congestion_ratio": congestion_ratio, "delayed_count": delayed_count, "total_scheduled": total_scheduled})

@function_tool
def get_long_haul_flights(airport_code: str) -> str:
    """
    Counts the number of scheduled departures that are long-haul (distance > 3000 KM) from the given airport.
    
    Args:
        airport_code: The ICAO or IATA code or name of the airport.
    """
    icao = _resolve_icao(airport_code)
    dep_url = f"{AEROAPI_BASE_URL}/airports/{icao}/flights/scheduled_departures"
    departures = _fetch_all_pages(dep_url, "scheduled_departures")
    
    if icao not in airports_icao:
        return json.dumps({"error": f"Airport {icao} not found in database to calculate origin coordinates."})
        
    origin_lat = airports_icao[icao]["lat"]
    origin_lon = airports_icao[icao]["lon"]
    
    long_haul_count = 0
    for flight in departures:
        dest = flight.get("destination", {})
        if not dest:
            continue
            
        dest_code = dest.get("code")
        if not dest_code:
            continue
            
        dest_icao = _resolve_icao(dest_code)
        if dest_icao in airports_icao:
            dest_lat = airports_icao[dest_icao]["lat"]
            dest_lon = airports_icao[dest_icao]["lon"]
            dist = haversine(origin_lat, origin_lon, dest_lat, dest_lon)
            if dist > 3000:
                long_haul_count += 1
                
    return json.dumps({"long_haul_count": long_haul_count, "total_scheduled_departures": len(departures)})

@function_tool
def calculate_airport_kpi(airport_code: str) -> str:
    """
    Calculates the overall KPI score for an airport based on total scheduled flights, congestion level, and long-haul flights.
    
    Args:
        airport_code: The ICAO or IATA code or name of the airport.
    """
    icao = _resolve_icao(airport_code)
    
    # 1. Total scheduled arrivals and departures
    arr_url = f"{AEROAPI_BASE_URL}/airports/{icao}/flights/scheduled_arrivals"
    dep_url = f"{AEROAPI_BASE_URL}/airports/{icao}/flights/scheduled_departures"
    arrivals = _fetch_all_pages(arr_url, "scheduled_arrivals")
    departures = _fetch_all_pages(dep_url, "scheduled_departures")
    total_scheduled = len(arrivals) + len(departures)
    
    normalized_flights = min(total_scheduled / 1000.0, 1.0)
    
    # 2. Congestion Level
    total_deps = len(departures)
    congestion_ratio = 0.0
    if total_deps > 0:
        delayed_count = sum(1 for flight in departures if flight.get("departure_delay", 0) > 0)
        congestion_ratio = delayed_count / total_deps
        
    # 3. Long-haul
    if icao not in airports_icao:
        return json.dumps({"error": f"Airport {icao} not found in database."})
        
    origin_lat = airports_icao[icao]["lat"]
    origin_lon = airports_icao[icao]["lon"]
    
    long_haul_count = 0
    for flight in departures:
        dest = flight.get("destination", {})
        if not dest:
            continue
        dest_code = dest.get("code")
        if dest_code:
            dest_icao = _resolve_icao(dest_code)
            if dest_icao in airports_icao:
                dest_lat = airports_icao[dest_icao]["lat"]
                dest_lon = airports_icao[dest_icao]["lon"]
                dist = haversine(origin_lat, origin_lon, dest_lat, dest_lon)
                if dist > 3000:
                    long_haul_count += 1
                    
    long_haul_ratio = 0.0
    if total_scheduled > 0:
        long_haul_ratio = long_haul_count / total_scheduled
        
    kpi_score = (normalized_flights * 0.4) + (congestion_ratio * 0.4) + (long_haul_ratio * 0.2)
    
    return json.dumps({
        "airport": icao,
        "kpi_score": kpi_score,
        "metrics": {
            "total_scheduled_flights": total_scheduled,
            "normalized_flights": normalized_flights,
            "congestion_ratio": congestion_ratio,
            "long_haul_count": long_haul_count,
            "long_haul_ratio": long_haul_ratio
        }
    })
