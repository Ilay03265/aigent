# Airport Investment Intelligence Agent

## Overview
This project is an AI agent designed to help analysts identify promising airport investment opportunities, such as terminal expansions and renovations. It uses public aviation APIs to gather data, applies deterministic scoring logic to rank airports, and provides a conversational interface for users to interact with the findings.

## Deliverables
- **Source Code**: Python-based implementation using Gradio and the OpenAI SDK.
- **Methodology & Architecture**: Documented below.

## Architecture
- **Frontend**: Gradio (for rapid UI prototyping and conversational interface).
- **Backend**: Python scripts orchestrating the logic.
- **LLM**: OpenAI SDK (for conversational understanding and tool calling).
- **Data Source**: Public Aviation API (TBD based on user selection).

## Scoring Methodology
The agent uses a deterministic scoring model rather than relying solely on LLM opinions. The core logic involves calculating an **Investment Score** based on factors such as:
1. **Flight Volume & Capacity**: High volume often indicates a need for expansion.
2. **Congestion Levels**: Delays or high utilization rates point to unmet demand.
3. **Route Types**: Percentage of long-haul vs short-haul flights.

*Detailed formula will be defined once the data API is finalized.*

## Key Tradeoffs
- **Gradio over Custom Web App**: Chosen for speed of development (1-day deliverable) to provide a functional chat UI immediately, trading off deep UI customization.
- **LLM Tool Calling over Pre-computed Database**: Real-time API fetching ensures data is up-to-date, trading off instantaneous response times for accuracy.
