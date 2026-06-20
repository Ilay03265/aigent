import os
from openai import OpenAI
from agents import Agent, Runner, trace, function_tool
from agent.tools import get_airport_flights, tool1, get_congestion_level, get_long_haul_flights, calculate_airport_kpi

# Initialize the client. It will automatically use the OPENAI_API_KEY from the environment.
client = OpenAI()

agent = Agent(
    name="Airport Intelligence Agent",
    model="gpt-4o-mini",
    instructions="You are an expert in airport planning, aviation analytics, and airport investment. Your goal is to help users identify airports that are strong candidates for terminal expansion based on congestion, unmet demand, and passenger traffic patterns.",
    tools=[get_airport_flights, tool1, get_congestion_level, get_long_haul_flights, calculate_airport_kpi]
)

async def chat_with_agent(message, chat_history):
    # Format the entire conversation history into a single text prompt to avoid schema errors
    history_text = "\n".join([
        f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}" 
        for msg in chat_history
    ])
    
    full_prompt = message
    if history_text.strip():
        full_prompt = f"Previous Conversation:\n{history_text}\n\nUser: {message}"

    # Runner.run automatically processes the message, triggers tools, and returns the final answer
    with trace("chat_with_agent"):
        response = await Runner.run(agent, full_prompt)
        
    return response.final_output
