from langchain_core.tools import tool
from utils.logger import logger
import requests
from typing import List,Any,Optional
from utils.configs import EXCHANGE_RATE_BASE_URL,EXCHANGE_RATE_API_KEY
from models.trip_state import ExchangeRate

def get_exchange_rate(from_currency: str, to_currency: str):
    try:
        response = requests.get(f"{EXCHANGE_RATE_BASE_URL}/{EXCHANGE_RATE_API_KEY}/latest/{from_currency}")
        response.raise_for_status()
        data = response.json()
        if data["result"] == "success" and to_currency in data["conversion_rates"]:
            rate = data["conversion_rates"][to_currency]
            return ExchangeRate(from_currency=from_currency, to_currency=to_currency, rate=rate)
        else:
            logger.error(f"Currency conversion failed: {data.get('error-type', 'Unknown error')}")
            raise ValueError(f"Could not get exchange rate from {from_currency} to {to_currency}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching exchange rate from {from_currency} to {to_currency}: {e}")
        raise

@tool
def get_exchange_rate_tool(from_currency: str, to_currency: str):
    """ Fetches the current exchange rate between two currencies."""
    return get_exchange_rate(from_currency,to_currency)        
    