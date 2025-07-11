from agents.base_agent import get_llm, logger
from tools.hotel_tools import real_Google_Hotels_tool 
from models.trip_state import TripState
from datetime import date

def hotel_finder_node(state: TripState) -> TripState:
    logger.info("\n--- Running Hotel Finder Agent ---")
    user_profile = state.get("user_profile")
    if not user_profile :
        logger.error("User profile or destination missing for hotel search.")
        return {**state, "error": "Destination missing for hotel search.", "status": "hotel_error"}

    destination = user_profile["destination"]
    start_date = user_profile["start_date"]
    end_date = user_profile["end_date"]
    budget_usd = user_profile.get("budget_usd", 1000.0) # Default budget if not parsed

    num_nights = (date.fromisoformat(end_date) - date.fromisoformat(start_date)).days
    if num_nights == 0: 
        num_nights = 1
    
    
    budget_per_night_max = (budget_usd * 0.5) / num_nights
    budget_per_night_min = budget_per_night_max * 0.5 

    try:
        
        hotel_suggestions = real_Google_Hotels_tool.invoke({
            "location": destination,
            "check_in_date": start_date,
            "check_out_date": end_date,
            "budget_min": budget_per_night_min,
            "budget_max": budget_per_night_max
        })
        logger.info(f"Hotel suggestions found: {len(hotel_suggestions)}")
        return {**state, "hotel_suggestions": hotel_suggestions, "status": "hotels_found"}
    except Exception as e:
        logger.error(f"Failed to find hotels for {destination}: {e}")
        return {**state, "error": f"Failed to find hotels for {destination}.", "status": "hotel_error"}