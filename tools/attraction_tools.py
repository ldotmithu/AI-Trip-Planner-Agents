from typing import List,Any,Optional
from langchain_core.tools import tool
from utils.configs import GOOGLE_PLACES_BASE_URL,GOOGLE_PLACES_API_KEY
from utils.logger import logger
import requests


def get_attraction_place(location:str,interests:List[str],num_results:int):
    
    endpoint = f"{GOOGLE_PLACES_BASE_URL}/textsearch/json"
    query = f"{location} attraction {" ".join(interests)}"
    params = {
        "query": query,
        "key": GOOGLE_PLACES_API_KEY,
        "rankby": "prominence", # Or "distance"
        "type": "point_of_interest" # Broad category
    }
    logger.warning("Real Google Places API implementation for attractions is a placeholder. Needs full implementation.")
    try:
        response = requests.get(endpoint,params=params)
        response.raise_for_status()
        data = response.json()
        attractions = []
        for result in data.get("results", [])[:num_results]:
            attractions.append({
                "name": result.get("name"),
                "type": result.get("types", ["unknown"])[0],
                "estimated_cost_usd": 0.0, 
                "address": result.get("formatted_address"),
                "place_id": result.get("place_id")
            })
        return attractions
    except Exception as e:
        logger.error(f"Error searching attractions: {e}")
        raise
    
@tool
def get_attraction_place_tool(location:str,interests:List[str],num_results:int):
    """ Searches for popular attractions and activities in a given location based on specified interests."""
    return get_attraction_place(location=location,interests=interests,num_results=num_results)

    