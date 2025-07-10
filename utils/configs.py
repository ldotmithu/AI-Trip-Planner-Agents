from dotenv import load_dotenv
import os 
load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
BOOKING_COM_API_KEY = os.getenv("BOOKING_COM_API_KEY")
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

WEATHER_BASE_URL = "http://api.weatherapi.com/v1" # WeatherAPI.com
GOOGLE_PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place"
BOOKING_COM_BASE_URL = "https://booking-com.p.rapidapi.com" # RapidAPI endpoint
EXCHANGE_RATE_BASE_URL = "https://v6.exchangerate-api.com/v6"

LLM_MODEL_NAME = "llama-3.3-70b-versatile" 
TEMPERATURE = 0.7





