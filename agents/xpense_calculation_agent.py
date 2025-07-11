from agents.base_agent import logger
from models.trip_state import TripState, ItineraryDay, Activity, Accommodation

def expense_calculation_node(state: TripState) -> TripState:
    logger.info("\n--- Running Expense Calculation Agent ---")
    current_itinerary = state.get("current_itinerary")
    user_profile = state.get("user_profile")

    if not current_itinerary:
        logger.warning("No itinerary found to calculate expenses.")
        return {**state, "total_estimated_cost_usd": 0.0, "status": "expenses_calculated"}
    if not user_profile:
        logger.warning("User profile missing for traveler count in expense calculation.")
        # Continue with assumption of 1 traveler if profile missing
        num_travelers = 1
    else:
        num_travelers = user_profile.get("number_of_travelers", 1)

    total_cost_usd = 0.0

    for day_plan in current_itinerary:
        # Sum costs for activities for all travelers
        for activity in day_plan.activities:
            cost = activity.estimated_cost_usd * num_travelers
            total_cost_usd += cost
            logger.debug(f"Adding activity cost: {activity.name} - {cost:.2f} USD")

        # Sum costs for accommodation (usually per room, not per person, adjust if your hotel API is per person)
        if day_plan.accommodation:
            # Assuming estimated_cost_usd_per_night for accommodation is per room
            accommodation_cost = day_plan.accommodation.estimated_cost_usd_per_night
            total_cost_usd += accommodation_cost
            logger.debug(f"Adding accommodation cost: {day_plan.accommodation.name} - {accommodation_cost:.2f} USD")

    logger.info(f"Total estimated cost in USD: {total_cost_usd:.2f}")
    return {**state, "total_estimated_cost_usd": total_cost_usd, "status": "expenses_calculated"}