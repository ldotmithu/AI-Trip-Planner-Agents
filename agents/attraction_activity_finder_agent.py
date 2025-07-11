# agents/attraction_activity_finder_agent.py
from agents.base_agent import get_llm, logger
from tools.attraction_tools import get_attraction_place_tool 
from models.trip_state import TripState

def attraction_activity_finder_node(state: TripState):
    logger.info("\n--- Running Attraction/Activity Finder Agent ---")
    user_profile = state.get("user_profile")
    if not user_profile :
        logger.error("User profile or destination missing for attraction search.")
        return {**state, "error": "Destination missing for attraction search.", "status": "attraction_error"}

    destination = user_profile["destination"]
    interests = user_profile.get("interests", ["popular"]) 

    try:
        attraction_suggestions = get_attraction_place_tool.invoke({
            "location": destination,
            "interests": interests,
            "num_results": 10 
        })
        logger.info(f"Attraction suggestions found: {len(attraction_suggestions)}")
        return {**state, "attraction_suggestions": attraction_suggestions, "status": "attractions_found"}
    except Exception as e:
        logger.error(f"Failed to find attractions for {destination}: {e}")
        return {**state, "error": f"Failed to find attractions for {destination}.", "status": "attraction_error"}