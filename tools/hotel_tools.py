from typing import List,Any,Optional
from utils.configs import BOOKING_COM_BASE_URL,BOOKING_COM_API_KEY
from utils.logger import logger
from datetime import date, timedelta
import requests
from langchain_core.tools import tool

def real_Google_Hotels(location: str, check_in_date: str, check_out_date: str, 
                       budget_min: float, budget_max: float):
    headers = {
        "X-RapidAPI-Key": BOOKING_COM_API_KEY,
        "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
    }
    query_string = {
        "adults_number": "1", 
        "checkin_date": check_in_date,
        "checkout_date": check_out_date,
        "filter_by_currency": "USD",
        "locale": "en-us",
        "order_by": "popularity",
        "room_number": "1", 
        "dest_type": "city",
        "dest_id": "-2205166" 
    }
   
    logger.warning("Real Hotel API implementation is a placeholder. Needs full implementation including dest_id lookup.")
    try:
        response = requests.get(f"{BOOKING_COM_BASE_URL}/v1/hotels/search", headers=headers, params=query_string)
        response.raise_for_status()
        data = response.json()
        hotels = []
        for h in data.get("result", [])[:5]:
            price_per_night = h.get("price_breakdown", {}).get("gross_price", {}).get("value") / ((date.fromisoformat(check_out_date) - date.fromisoformat(check_in_date)).days or 1)
            if price_per_night and budget_min <= price_per_night <= budget_max:
                hotels.append({
                    "name": h.get("hotel_name"),
                    "price_per_night_usd": price_per_night,
                    "rating": h.get("review_score"),
                    "address": h.get("address")
                })
        return hotels
    except Exception as e:
        logger.error(f"Error searching hotels: {e}")
        raise

@tool
def real_Google_Hotels_tool(location: str, check_in_date: str, check_out_date: str, budget_min: float, budget_max: float):
    """ Searches for hotels in a given location for specified dates and within a budget range"""
    return real_Google_Hotels(location, check_in_date, check_out_date, budget_min, budget_max)

    
