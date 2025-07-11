from utils.logger import logger
import requests
import re
from agents.base_agent import get_llm
from models.trip_state import TripState,UserProfile
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from datetime import date,timedelta

# output must json type 
user_profile_parser  = PydanticOutputParser(pydantic_object=UserProfile)

input_parser_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are an expert travel assistant. Your task is to extract key travel details from a user's query.\n"
         "Extract the destination, start date, end date, user interests, approximate budget in USD, and preferred currency for display. "
         "If no budget is specified, default to 1000 USD. If no preferred currency, default to USD. "
         "If dates are relative (e.g., 'next week', 'tomorrow'), convert them to specific YYYY-MM-DD dates. "
         "If number of travelers is not specified, assume 1.\n"
         "Always respond with a JSON object conforming to the UserProfile schema. "
         "If information is missing, use reasonable defaults or indicate as unknown if not applicable.\n"
         "Current date: {current_date}\n\n"
         "{format_instructions}"
        ),
        ("human", "{user_input}")
    ]
)


def parse_relative_dates(text: str, current_date: date):
    start_date = current_date
    end_date = current_date

    lower_text = text.lower()
    if "today" in lower_text:
        start_date = current_date
        end_date = current_date
    elif "tomorrow" in lower_text:
        start_date = current_date + timedelta(days=1)
        end_date = current_date + timedelta(days=1)
    elif "next week" in lower_text:
        start_date = current_date + timedelta(days=(7 - current_date.weekday()) % 7) 
        end_date = start_date + timedelta(days=6)
    elif "next month" in lower_text:
        start_date = (current_date.replace(day=1) + timedelta(days=31)).replace(day=1)
        end_date = start_date + timedelta(days=29) 

    
    import re
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    dates_found = date_pattern.findall(text)
    if len(dates_found) == 1:
        start_date = date.fromisoformat(dates_found[0])
        end_date = start_date # Assume single day if only one date
    elif len(dates_found) >= 2:
        start_date = date.fromisoformat(dates_found[0])
        end_date = date.fromisoformat(dates_found[1])

    return start_date.isoformat(), end_date.isoformat()

def input_parser_node(state: TripState) -> TripState:
    logger.info("\n--- Running Input Parser Agent ---")
    user_input = state["user_input"]
    current_date = date.today()

    chain = input_parser_prompt | get_llm() | user_profile_parser

    try:
        raw_profile = chain.invoke({
            "user_input": user_input,
            "current_date": current_date.isoformat(),
            "format_instructions": user_profile_parser.get_format_instructions()
        })

        start_date_str, end_date_str = parse_relative_dates(user_input, current_date)
        
        user_profile_data = raw_profile.dict()
        user_profile_data['start_date'] = start_date_str
        user_profile_data['end_date'] = end_date_str
        user_profile_data['budget_usd'] = float(user_profile_data.get('budget_usd', 1000.0))
        user_profile_data['preferred_currency'] = user_profile_data.get('preferred_currency', 'USD').upper()
        user_profile_data['number_of_travelers'] = int(user_profile_data.get('number_of_travelers', 1))

        if not user_profile_data.get("destination"):
            raise ValueError("Destination could not be parsed. Please provide a clear destination.")
        if date.fromisoformat(user_profile_data['start_date']) > date.fromisoformat(user_profile_data['end_date']):
            user_profile_data['start_date'], user_profile_data['end_date'] = user_profile_data['end_date'], user_profile_data['start_date']
        
        user_profile = UserProfile(**user_profile_data)

        logger.info(f"Parsed User Profile: {user_profile.dict()}")
        return {**state, "user_profile": user_profile, "status": "profile_parsed"}
    except Exception as e:
        logger.error(f"Error parsing user input: {e}")
        return {**state, "error": f"Failed to parse your input: {e}. Please try again with a clearer query.", "status": "input_parse_error"}