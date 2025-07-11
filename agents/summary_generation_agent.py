# agents/summary_generation_agent.py
from agents.base_agent import get_llm, logger
from models.trip_state import TripState, UserProfile, ItineraryDay, WeatherInfo, ExchangeRate
from langchain_core.prompts import ChatPromptTemplate
from datetime import date

def summary_generation_node(state: TripState) -> TripState:
    logger.info("\n--- Running Summary Generation Agent ---")
    user_profile = state.get("user_profile")
    itinerary = state.get("current_itinerary")
    weather = state.get("weather_info")
    total_cost_usd = state.get("total_estimated_cost_usd")
    total_cost_local = state.get("total_estimated_cost_local_currency")
    currency_rates = state.get("currency_rates")

    llm = get_llm()

    summary_parts = []

    if user_profile:
        summary_parts.append(f"**Trip Plan for {user_profile.destination}**\n")
        summary_parts.append(f"Dates: {user_profile.start_date} to {user_profile.end_date} "
                             f"({(date.fromisoformat(user_profile.end_date) - date.fromisoformat(user_profile.start_date)).days + 1} days)")
        summary_parts.append(f"Travelers: {user_profile.number_of_travelers}")
        summary_parts.append(f"Interests: {', '.join(user_profile.interests)}")
        summary_parts.append(f"Budget: {user_profile.budget_usd:.2f} USD")
    else:
        summary_parts.append("**Trip Plan Summary** (Some initial details might be missing)\n")

    if weather and weather.forecast:
        summary_parts.append("\n**Weather Forecast:**")
        for day_forecast in weather.forecast:
            summary_parts.append(f"- {day_forecast.date}: Max {day_forecast.max_temp_c}°C, Min {day_forecast.min_temp_c}°C, {day_forecast.condition}")
    elif weather and weather.current_weather:
         summary_parts.append(f"\n**Current Weather in {weather.current_weather.city}:** {weather.current_weather.temp_c}°C, {weather.current_weather.condition}")

    if itinerary:
        summary_parts.append("\n**Detailed Itinerary:**")
        for day_plan in itinerary:
            summary_parts.append(f"\n--- Day: {day_plan.date} ---")
            for activity in day_plan.activities:
                cost_str = f" (${activity.estimated_cost_usd:.2f} per person)" if activity.estimated_cost_usd > 0 else ""
                summary_parts.append(f"- {activity.time or 'Anytime'}: {activity.name} ({activity.type}){cost_str}")
                if activity.details:
                    summary_parts.append(f"  *Details*: {activity.details}")
            if day_plan.accommodation:
                summary_parts.append(f"Accommodation: {day_plan.accommodation.name} (Est. ${day_plan.accommodation.estimated_cost_usd_per_night:.2f}/night)")
                if day_plan.accommodation.rating:
                    summary_parts.append(f"  *Rating*: {day_plan.accommodation.rating}/5")
    else:
        summary_parts.append("\nNo detailed itinerary could be generated at this time. Please check your query or budget.")

    if total_cost_usd is not None:
        summary_parts.append(f"\n**Estimated Total Expenses:**")
        summary_parts.append(f"- In USD: ${total_cost_usd:.2f}")
        if total_cost_local is not None and currency_rates:
            summary_parts.append(f"- In {currency_rates.to_currency}: {total_cost_local:.2f} {currency_rates.to_currency} (Rate: 1 USD = {currency_rates.rate:.2f} {currency_rates.to_currency})")
        elif total_cost_local is not None:
            summary_parts.append(f"- In local currency: {total_cost_local:.2f} (Currency conversion might have been skipped or failed).")

    final_summary_text = "\n".join(summary_parts)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful travel assistant. Summarize the provided trip details in a clear, concise, and engaging manner. Highlight key information and make it easy to read. Use Markdown for formatting."),
        ("human", "Here are the trip details:\n\n{trip_details}")
    ])

    try:
        response = llm.invoke(prompt.format_messages(trip_details=final_summary_text))
        summary = response.content
        logger.info("Summary generated successfully.")
        return {**state, "agent_response": summary, "status": "summary_generated"}
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return {**state, "error": f"Failed to generate final summary: {e}.", "status": "summary_error"}