from agents.base_agent import logger
from tools.currency_tools import get_exchange_rate_tool
from models.trip_state import TripState, ExchangeRate

def currency_conversion_node(state: TripState) -> TripState:
    logger.info("\n--- Running Currency Conversion Agent ---")
    total_cost_usd = state.get("total_estimated_cost_usd")
    user_profile = state.get("user_profile")

    if total_cost_usd is None:
        logger.warning("No total USD cost found for currency conversion.")
        return {**state, "total_estimated_cost_local_currency": None, "status": "currency_conversion_skipped"}
    if not user_profile or not user_profile.get("preferred_currency"):
        logger.warning("Preferred currency missing. Skipping conversion.")
        return {**state, "total_estimated_cost_local_currency": total_cost_usd, "status": "currency_conversion_skipped"}

    preferred_currency = user_profile["preferred_currency"].upper() # Ensure uppercase
    if preferred_currency == "USD": # No conversion needed if already USD
        logger.info("Preferred currency is USD, no conversion needed.")
        return {**state, "total_estimated_cost_local_currency": total_cost_usd, "currency_rates": ExchangeRate(from_currency="USD", to_currency="USD", rate=1.0), "status": "currency_converted"}

    try:
        exchange_rate_obj = get_exchange_rate_tool.invoke({
            "from_currency": "USD",
            "to_currency": preferred_currency
        })

        if exchange_rate_obj and exchange_rate_obj.rate > 0:
            converted_cost = total_cost_usd * exchange_rate_obj.rate
            logger.info(f"Converted {total_cost_usd:.2f} USD to {converted_cost:.2f} {preferred_currency} at rate {exchange_rate_obj.rate:.2f}")
            return {
                **state,
                "total_estimated_cost_local_currency": converted_cost,
                "currency_rates": exchange_rate_obj,
                "status": "currency_converted"
            }
        else:
            logger.error(f"Failed to get a valid exchange rate for {preferred_currency}.")
            return {**state, "error": f"Could not convert to {preferred_currency}. Displaying in USD.", "status": "currency_conversion_error"}

    except Exception as e:
        logger.error(f"Error during currency conversion: {e}")
        return {**state, "error": f"Failed to convert currency: {e}. Displaying in USD.", "status": "currency_conversion_error"}