# agents/itinerary_planning_agent.py
from agents.base_agent import get_llm, logger
from models.trip_state import TripState, ItineraryDay, Activity, Accommodation, WeatherInfo, UserProfile
from datetime import date, timedelta
from typing import List
import json
from langchain_core.prompts import ChatPromptTemplate

def itinerary_planning_node(state: TripState) -> TripState:
    logger.info("\n--- Running Itinerary Planning Agent ---")
    user_profile = state.get("user_profile")
    attraction_suggestions = state.get("attraction_suggestions", [])
    hotel_suggestions = state.get("hotel_suggestions", [])
    weather_info = state.get("weather_info")

    if not user_profile:
        return {**state, "error": "User profile missing for itinerary planning.", "status": "itinerary_error"}

    llm = get_llm()


    itinerary_day_schema = ItineraryDay.schema_json(indent=2)
    activity_schema = Activity.schema_json(indent=2)
    accommodation_schema = Accommodation.schema_json(indent=2)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert travel itinerary planner. Your task is to create a detailed daily itinerary "
         "based on user preferences, available attractions, suggested hotels, and weather forecasts.\n\n"
         "User Profile:\n{user_profile}\n\n"
         "Attraction Suggestions:\n{attraction_suggestions_str}\n\n"
         "Hotel Suggestions:\n{hotel_suggestions_str}\n\n"
         "Weather Forecast:\n{weather_forecast_str}\n\n"
         "Rules for Itinerary Planning:\n"
         "- Create a day-by-day plan from start_date to end_date (inclusive).\n"
         "- For each day, suggest 2-4 activities. Prioritize activities based on user interests.\n"
         "- Consider weather: Suggest indoor activities if rain is forecasted. Suggest outdoor if sunny.\n"
         "- Estimate cost for each activity in USD. If unknown, use a reasonable estimate (e.g., $10-$30 for entry, $0 for parks/beaches).\n"
         "- Include a suggested accommodation for each night. Prioritize hotels that fit the budget and have good ratings. Pick ONE best hotel per night.\n"
         "- For the last night, the accommodation should be the same as the previous nights or null if it's a single day trip.\n"
         "- Provide brief details/descriptions for each activity and accommodation.\n"
         "- Ensure activities are geographically reasonable for a single day (e.g., don't put attractions far apart on the same day if time is limited).\n"
         "- Respond with a JSON array where each element conforms to the ItineraryDay Pydantic schema.\n\n"
         "ItineraryDay Schema:\n```json\n" + itinerary_day_schema + "\n```\n"
         "Activity Schema:\n```json\n" + activity_schema + "\n```\n"
         "Accommodation Schema:\n```json\n" + accommodation_schema + "\n```\n"
         "Ensure the JSON output is a valid array of ItineraryDay objects."
        ),
        ("human", "Generate the detailed trip itinerary.")
    ])

    attractions_str = json.dumps(attraction_suggestions, indent=2)
    hotels_str = json.dumps(hotel_suggestions, indent=2)
    weather_str = json.dumps(weather_info.dict() if weather_info else {}, indent=2)

    
    start_date = date.fromisoformat(user_profile.start_date)
    end_date = date.fromisoformat(user_profile.end_date)
    num_days = (end_date - start_date).days + 1

    
    chosen_accommodation = None
    if hotel_suggestions:
        affordable_hotels = [h for h in hotel_suggestions if h.get("price_per_night_usd", 0) <= user_profile.budget_usd]
        if affordable_hotels:
            chosen_accommodation_dict = sorted(affordable_hotels, key=lambda x: x.get("rating", 0), reverse=True)[0]
            chosen_accommodation = Accommodation(
                name=chosen_accommodation_dict.get("name", "Unknown Hotel"),
                estimated_cost_usd_per_night=chosen_accommodation_dict.get("price_per_night_usd", 0.0),
                details=f"Rating: {chosen_accommodation_dict.get('rating')}",
                rating=chosen_accommodation_dict.get("rating"),
                address=chosen_accommodation_dict.get("address")
            )
        else:
            logger.warning("No hotels found within budget range.")
            chosen_accommodation = Accommodation(name="No suitable hotel found within budget", estimated_cost_usd_per_night=0.0)
    else:
        chosen_accommodation = Accommodation(name="No hotel suggestions available", estimated_cost_usd_per_night=0.0)


    try:
        response = llm.invoke(prompt.format_messages(
            user_profile=user_profile.dict(),
            attraction_suggestions_str=attractions_str,
            hotel_suggestions_str=hotels_str,
            weather_forecast_str=weather_str
        ))
        
        itinerary_json_str = response.content.strip()
        
        parsed_itinerary_data = json.loads(itinerary_json_str)
        
        planned_itinerary = []
        for day_data in parsed_itinerary_data:
            # Ensure accommodation is passed correctly, if chosen_accommodation is not None
            if chosen_accommodation and day_data.get("accommodation") is None:
                day_data["accommodation"] = chosen_accommodation.dict()
            elif chosen_accommodation and day_data.get("accommodation"):
                # If LLM suggested something, merge/prefer if it's better, or override
                pass # For now, let LLM override if it chose something, or keep chosen_accommodation
            
            # Make sure activities have a reasonable cost if missing
            for activity in day_data.get("activities", []):
                if activity.get("estimated_cost_usd") is None:
                    activity["estimated_cost_usd"] = 0.0 # Default to free if LLM didn't estimate
            
            planned_itinerary.append(ItineraryDay(**day_data))

        logger.info(f"Itinerary planned for {len(planned_itinerary)} days.")
        return {**state, "current_itinerary": planned_itinerary, "status": "itinerary_planned"}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse itinerary JSON: {e}\nRaw LLM output:\n{itinerary_json_str}")
        return {**state, "error": f"Failed to plan itinerary due to output format issue: {e}. Please try again.", "status": "itinerary_error"}
    except Exception as e:
        logger.error(f"Error planning itinerary: {e}")
        return {**state, "error": f"Failed to plan itinerary: {e}.", "status": "itinerary_error"}