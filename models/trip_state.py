from pydantic import BaseModel,Field
from typing import TypedDict,List,Optional,Dict,Any
from datetime import date

class UserProfile(BaseModel):
    destination: str = Field(description="The desired travel destination.")
    start_date: str = Field(description="Start date of the trip in YYYY-MM-DD format.")
    end_date: str = Field(description="End date of the trip in YYYY-MM-DD format.")
    interests: List[str] = Field(description="List of user interests, e.g., ['culture', 'beaches', 'food'].")
    budget_usd: float = Field(description="Total budget for the trip in USD.")
    preferred_currency: str = Field(description="User's preferred local currency code, e.g., 'LKR', 'USD', 'EUR'.")
    number_of_travelers: int = Field(default=1, description="Number of people traveling.")

class Activity(BaseModel):
    name: str = Field(description="Name of the activity or attraction.")
    type: str = Field(description="Type of activity, e.g., 'museum', 'beach', 'restaurant'.")
    time: Optional[str] = Field(description="Suggested time of day for the activity, e.g., '10:00 AM', 'Afternoon'.")
    estimated_cost_usd: float = Field(description="Estimated cost of the activity in USD.")
    details: Optional[str] = Field(description="Brief description or additional details about the activity.")
    address: Optional[str] = Field(description="Address of the activity.")

class Accommodation(BaseModel):
    name: str = Field(description="Name of the hotel or accommodation.")
    estimated_cost_usd_per_night: float = Field(description="Estimated cost per night in USD.")
    details: Optional[str] = Field(description="Brief details about the accommodation.")
    rating: Optional[float] = Field(description="Rating of the accommodation.")
    address: Optional[str] = Field(description="Address of the accommodation.")

class ItineraryDay(BaseModel):
    date: str = Field(description="Date of the itinerary day in YYYY-MM-DD format.")
    activities: List[Activity] = Field(default_factory=list, description="List of planned activities for the day.")
    accommodation: Optional[Accommodation] = Field(description="Accommodation planned for the night.")
    
class WeatherCondition(BaseModel):
    city: str = Field(description="City name.")
    temp_c: float = Field(description="Temperature in Celsius.")
    condition: str = Field(description="Weather condition description.")

class ForecastDay(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format.")
    max_temp_c: float = Field(description="Maximum temperature in Celsius.")
    min_temp_c: float = Field(description="Minimum temperature in Celsius.")
    condition: str = Field(description="Weather condition description.")

class WeatherInfo(BaseModel):
    current_weather: Optional[WeatherCondition]
    forecast: Optional[List[ForecastDay]]

class ExchangeRate(BaseModel):
    from_currency: str = Field(description="Base currency code, e.g., 'USD'.")
    to_currency: str = Field(description="Target currency code, e.g., 'LKR'.")
    rate: float = Field(description="Exchange rate (1 FROM_CURRENCY = X TO_CURRENCY).")      
    

class TripState(TypedDict):
    user_input: str
    user_profile: Optional[UserProfile]
    current_itinerary: Optional[List[ItineraryDay]]
    weather_info: Optional[WeatherInfo]
    attraction_suggestions: Optional[List[Dict[str, Any]]] 
    hotel_suggestions: Optional[List[Dict[str, Any]]]     
    currency_rates: Optional[ExchangeRate]
    total_estimated_cost_usd: Optional[float]
    total_estimated_cost_local_currency: Optional[float]
    agent_response: Optional[str] 
    status: str
    error: Optional[str] 
    retry_count: int    
    
      
        
        
    