from utils.configs import WEATHER_BASE_URL,WEATHER_API_KEY
from tools.base_tool import *
from models.trip_state import WeatherCondition,ForecastDay
from datetime import date
import os 
from langchain_core.tools import tool
import requests
from typing import List

def get_current_weather(location:str):
    """get the current weather using api"""
    try:
        response = requests.get(
            f"{WEATHER_BASE_URL}/current.json?key={WEATHER_API_KEY}&q={location}&aqi=yes"
        )
        response.raise_for_status()
        data = response.json()
        return WeatherCondition(
            city=data["location"]["name"],
            temp_c=data["current"]["temp_c"],
            condition=data["current"]["condition"]["text"]
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching current weather for {location}: {e}")
        raise
def get_forecast_weather(location:str,days:int=3):
   """get the forecast weather using api""" 
   try:
        response = requests.get(
            f"{WEATHER_BASE_URL}/forecast.json?key={WEATHER_API_KEY}&q={location}&days={days}&aqi=yes&alerts=no"
        )
        response.raise_for_status()
        data = response.json()
        forecast_days=[]
        for day in data["forecast"]["forecastday"]:
            forecast_days.append(
                ForecastDay(
                    date=day["date"],
                    max_temp_c=day["day"]["maxtemp_c"],
                    min_temp_c=day["day"]["mintemp_c"],
                    condition=day["day"]["condition"]["text"]
                )
            )
        return forecast_days     
   except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching forecast weather for {location}: {e}")
        raise

@tool
def get_current_weather_tool(location:str):
    """Fetches the current weather conditions for a given location"""
    return get_current_weather(location=location)

@tool
def get_forecast_weather_tool(location:str ,days:int=3):
    """Fetches the weather forecast for a given location for the next few days."""
    return get_forecast_weather(location=location,days=days)

## testing 

# if __name__ == "__main__":
#     try:
#         current_w = get_current_weather_tool.invoke({"location": "London"})
#         print(f"Current weather: {current_w.dict()}")

#         forecast_w = get_forecast_weather_tool.invoke({"location": "London", "num_days": 5})
#         print(f"Forecast weather: {[f.dict() for f in forecast_w]}")
#     except Exception as e:
#         print(f"An error occurred: {e}")     
   
    