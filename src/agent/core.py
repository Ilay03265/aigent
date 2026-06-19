import os
from openai import OpenAI
from agents import Agent, Runner, trace

# Initialize the client. It will automatically use the OPENAI_API_KEY from the environment.
# client = OpenAI()

def chat_with_agent(message, chat_history):
    """
    This function will interact with the OpenAI API.
    For now, it returns a placeholder response.
    """
    # TODO: Implement OpenAI SDK tool calling logic here
    # Example flow:
    # 1. Send user message and history to OpenAI
    # 2. If OpenAI calls a tool (e.g., get_airport_data), execute the tool from api_client.py
    # 3. Apply scoring logic from scoring.py if needed
    # 4. Return final response to the user
    
    return "I am the Airport Investment Intelligence Agent. I am still being built! You said: " + message
