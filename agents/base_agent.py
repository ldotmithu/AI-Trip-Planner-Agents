from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from utils.logger import logger
from utils.configs import LLM_MODEL_NAME, TEMPERATURE


def get_llm():
    """Initializes and returns the ChatOpenAI LLM."""
    return ChatGroq(model=LLM_MODEL_NAME,temperature=TEMPERATURE)

def append_message_to_state(state: dict, message: BaseMessage, key: str = "messages") -> dict:
    current_messages = state.get(key, [])
    return {**state, key: current_messages + [message]}

