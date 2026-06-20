from agents import Agent, WebSearchTool, ModelSettings


# --- 1. Search Agent ---
SEARCH_INSTRUCTIONS = (
    "You are a research assistant. You will receive a specific web search plan from the Planner Agent, "
    "containing queries specifically formatted to search within targeted domains (e.g., 'query site:example.com'). "
    "Execute all of these specific searches using your WebSearchTool. "
    "Produce a concise summary of the results in 2-3 paragraphs and less than 300 words. "
    "Capture the main points. Write succinctly, no need for complete sentences. "
    "Ignore fluff and do not include additional commentary."
)

search_agent = Agent(
    name="Search Agent",
    instructions=SEARCH_INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)


# --- 2. Planner Agent ---
HOW_MANY_DOMAINS = 3

PLANNER_INSTRUCTIONS = (
    f"You are a strategic research planner. Given a user query, your task is to identify "
    f"exactly {HOW_MANY_DOMAINS} highly authoritative website domains to answer the query.\n"
    f"For each domain, formulate a precise search query using the 'site:' operator "
    f"(For example: 'artificial intelligence site:ibm.com').\n"
    f"Once you have formulated the {HOW_MANY_DOMAINS} domain-specific queries, you MUST "
    f"transfer control to the 'Search Agent' and pass the queries to it so it can execute the searches."
)

planner_agent = Agent(
    name="Planner Agent",
    instructions=PLANNER_INSTRUCTIONS,
    model="gpt-4o-mini",
    handoffs=[search_agent] # הסוכן מקבל את סוכן החיפוש ככלי מעבר
)
