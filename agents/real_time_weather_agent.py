from agents.base_agent import get_llm, logger
from tools.weather_tools import get_current_weather_tool,get_forecast_weather_tool
from models.trip_state import TripState, WeatherInfo
from datetime import date,timedelta,time

def weather_info_node(state:TripState):
    logger.info("\n--- Running Real-Time Weather Agent ---")
    user_profile = state.get("user_profile")
    if not user_profile:
        logger.error("User profile or destination missing for weather check.")
        return {**state, "error": "Destination missing for weather check.", "status": "weather_error"}
    
    location = user_profile["destination"]
    
    #forecast days
    start_date = date.fromisoformat(user_profile["start_date"])
    end_date = date.fromisoformat(user_profile["end_date"])
    num_days = (end_date - start_date).days + 1
    
    num_days = min(num_days, 3)
    
    try:
        current_weather = get_current_weather_tool.invoke({"location":location})
        forecast_weather = get_forecast_weather_tool.invoke({"location":location,"days":num_days})
        
        weather_info = WeatherInfo(
            current_weather=current_weather if current_weather else None,
            forecast=forecast_weather if forecast_weather else []
        )
        logger.info(f"Weather fetched for {location}: {weather_info.dict()}")
        return {**state, "weather_info": weather_info, "status": "weather_checked"}
    
    except Exception as e:
        logger.error(f"Failed to get weather info for {location}: {e}")
        return {**state, "error": f"Failed to retrieve weather information for {location}.", "status": "weather_error"}
    