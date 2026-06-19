import os
# pyrefly: ignore [missing-import]
import gradio as gr
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

from agent.core import chat_with_agent

# Load environment variables
load_dotenv()

def respond(message, chat_history):
    # This function will handle the chat history and agent response
    response = chat_with_agent(message, chat_history)
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": response})
    return "", chat_history

with gr.Blocks(title="Airport Investment Intelligence") as demo:
    gr.Markdown("# ✈️ Airport Investment Intelligence Agent")
    gr.Markdown("Ask me about airport congestion, unmet flight demand, or candidates for terminal expansion.")
    
    chatbot = gr.Chatbot(height=500)
    msg = gr.Textbox(label="Message", placeholder="e.g., Which airports in New England are strong candidates for terminal expansion?")
    clear = gr.ClearButton([msg, chatbot])

    msg.submit(respond, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch()
