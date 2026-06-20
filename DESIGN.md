# Airgate AI - Design Document

## 1. System Overview
Airgate AI is an agentic system designed to help users identify strong candidates for airport terminal expansion or investment. By leveraging the FlightAware AeroAPI and a specialized set of LLM tools, the agent analyzes flight volumes, operational congestion, and strategic importance (long-haul routes) to calculate an investment KPI.

* **User Interface**: Chat-based conversational UI with gradio.
* **Agent Core**: LLM evaluating user intent and sequencing tool execution using openai-agents SDK.
* **Tooling Layer**: Python-based @function_tool methods handling deterministic logic for KPI calculation and data processing, web search for additional information using Google SERP API.
* **Data Layer**: External FlightAware AeroAPI and local static airport datasets.

## 2. Scoring Methodology (KPI)
The KPI is designed to highlight airports experiencing operational strain while still prioritizing significant hubs. The scoring formula is scaled from `0.0` to `1.0` based on the following weighted components:

**Formula:**
`KPI Score = (Normalized Volume × 0.4) + (Congestion Ratio × 0.4) + (Long-haul Ratio × 0.2)`

### 2.1 Volume Metric (40% Weight)
- **Calculation:** `min(Total Scheduled Arrivals + Departures / 1000, 1.0)`
- **Rationale:** Measures the absolute size and traffic of the airport. We divide by a baseline of 1,000 flights to normalize the value. Using a `min` function ensures that once an airport reaches "mega-hub" status (1000+ flights), it receives the maximum volume score, preventing it from completely dwarfing mid-sized, highly congested airports.

### 2.2 Congestion Ratio (40% Weight)
- **Calculation:** `Delayed Departures / Total Scheduled Departures`
- **Rationale:** Identifies operational strain. Airports with a high percentage of delayed flights often indicate unmet capacity, poor infrastructure scaling, or severe gate constraints—prime indicators that terminal expansion or capital investment is necessary.

### 2.3 Long-haul Capability (20% Weight)
- **Calculation:** `Flights > 3000 KM / Total Scheduled Departures`
- **Rationale:** Evaluates the strategic value and international reach of the airport. Long-haul flights require specific infrastructure (larger gates, longer runways, extensive customs facilities). A high ratio indicates a premium hub.

---

## 3. Key Technical Tradeoffs

### 3.1 Local Distance Calculation vs. API Route Query
To identify long-haul flights (> 3000 KM), the system calculates the great-circle distance between origin and destination coordinates using a local `airportsdata` dictionary and the Haversine formula.
- **Pros:** Massive reduction in API calls and associated costs. Zero network latency for route calculations.
- **Cons:** Great-circle distance is a straight-line approximation. It does not account for actual filed flight paths, wind patterns, or no-fly zones. Flights sitting exactly on the 3000 KM threshold might be slightly misclassified.

### 3.2 Scheduled Endpoints vs. Historic Analytics
The system relies on the AeroAPI `scheduled_departures` and `scheduled_arrivals` endpoints to calculate immediate congestion and volume.
- **Pros:** Provides an accurate, real-time snapshot of current operational stress with a minimal number of API queries.
- **Cons:** It captures delays active in the current schedule window rather than a rolling historic average. Seasonal fluctuations or temporary weather events could artificially skew an airport's KPI on a given day.

### 3.3 Agentic Tooling vs. Deterministic Scripting
Rather than running a fixed data pipeline that ranks all airports in a spreadsheet, the logic is encapsulated as discrete `@function_tool` methods accessible to a conversational LLM agent.
- **Pros:** Maximum flexibility. Users can ask qualitative questions ("Compare the congestion at JFK vs LHR and search the web for recent infrastructure news at the worse one"). The agent can dynamically decide which tools to run based on the user's inquiry.
- **Cons:** LLMs introduce latency when sequencing tool calls and require careful prompt engineering to ensure they do not hallucinate the math when interpreting the JSON outputs. To mitigate this, the heavy KPI calculations are done deterministically in Python before being handed back to the LLM.

### 3.4 Data Fidelity vs. API Cost
FlightAware's AeroAPI provides high-fidelity, real-time aviation data, but it operates on a pay-per-query model that can become expensive if an LLM agent queries it aggressively.
* **Pros:** Guarantees the agent has access to the most accurate, up-to-date schedule and delay metrics.
* **Cons:** High operational cost. If a user asks a broad question (e.g., "Compare all airports in New England"), the agent might trigger dozens of expensive tool calls. To mitigate this, the architecture limits the scope of API tools to specific airport codes and relies on local/deterministic calculations (like the Haversine formula) whenever possible to minimize external network requests.

---

## 4. Assumptions, Uncertainty, and Scoping

### 4.1 Assumptions
* **Delay = Demand:** The primary assumption of the KPI is that a high ratio of delayed departures strongly correlates with infrastructure strain (lack of gates, runway congestion) rather than anomalous events.
* **Volume Baseline:** We assume a baseline of 1,000 flights represents a mature hub, capping the volume score so mid-sized airports still have a chance to rank high based on congestion.

### 4.2 Uncertainty
* **Cause of Congestion:** The data cannot distinguish between delays caused by weather (e.g., a snowstorm in Anchorage) versus delays caused by structural capacity limits. This introduces uncertainty into whether an airport *actually* needs terminal expansion or just had a bad weather day.
* **LLM Tool Chaining:** While the scoring logic is deterministic, the agent's interpretation of the user's prompt is non-deterministic. There is minor uncertainty in how the LLM might sequence its tool calls for highly complex, multi-part questions.

### 4.3 Scoping
* **Current Schedules Only:** The tool is currently scoped to analyze near-term scheduled flights and immediate operational metrics. It does not scope in multi-year historical trend analysis, passenger demographics, or financial revenue data of the airports.
* **Geographical Scope:** The agent is designed to evaluate US-based airports (as requested by the firm's investment focus) but can technically evaluate international hubs if the appropriate ICAO/IATA codes are provided.
