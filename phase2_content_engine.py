# phase2_content_engine.py
# langgraph state machine for autonomous bot post generation

import os, json
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"), temperature=0.8)

BOT_PERSONAS = {
    "bot_a": "You are a tech maximalist. You believe AI and crypto will solve all human problems. You are highly optimistic about technology, Elon Musk, and space exploration. You dismiss regulatory concerns. You post with confidence and sometimes arrogance.",
    "bot_b": "You are a doomer and skeptic. You believe late-stage capitalism and tech monopolies are destroying society. You are highly critical of AI, social media, and billionaires. You value privacy and nature. You post with righteous anger.",
    "bot_c": "You are a finance bro. You strictly care about markets, interest rates, trading algorithms, and making money. You speak in finance jargon and view everything through the lens of ROI. You post like you're on a trading floor.",
}

@tool
def mock_searxng_search(query:str)->str:
    """mock web search tool that returns hardcoded headlines based on keywords"""
    q = query.lower()
    if "crypto" in q or "bitcoin" in q:
        return "Bitcoin hits new all-time high amid regulatory ETF approvals. Crypto market cap crosses $3 trillion again."
    elif "ai" in q or "openai" in q or "llm" in q:
        return "OpenAI releases GPT-5 with autonomous agent capabilities. Tech stocks surge as AI spending hits $500B."
    elif "market" in q or "stock" in q or "rate" in q:
        return "Fed signals rate cuts paused amid sticky inflation. S&P 500 drops 1.2% on weak jobs data."
    elif "climate" in q or "nature" in q or "environment" in q:
        return "UN report: 2025 is hottest year on record. Tech industry carbon footprint doubles due to AI data centers."
    elif "elon" in q or "tesla" in q or "space" in q:
        return "SpaceX Starship completes first commercial orbital mission. Elon Musk announces Mars colony timeline for 2029."
    else:
        return "Breaking: Global tech summit debates AI regulation. World leaders divided on open-source vs closed AI models."

# --- graph state ---
class BotState(TypedDict):
    bot_id: str
    persona: str
    search_query: str
    search_results: str
    post_content: str
    topic: str

# --- node 1: decide what to search ---
def decide_search(state:BotState)->BotState:
    persona = state["persona"]
    prompt = f"""You are this bot: {persona}

Decide what topic you want to post about today. Then write a short search query (max 5 words) to find relevant news.

Respond in JSON only, no markdown:
{{"topic": "...", "search_query": "..."}}"""

    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip()
    # strip markdown fences if model adds them
    raw = raw.replace("```json","").replace("```","").strip()
    parsed = json.loads(raw)
    state["topic"] = parsed["topic"]
    state["search_query"] = parsed["search_query"]
    print(f"\n[NODE 1] bot: {state['bot_id']}")
    print(f"[NODE 1] topic: {state['topic']}")
    print(f"[NODE 1] search query: {state['search_query']}")
    return state

# --- node 2: run mock search ---
def web_search(state:BotState)->BotState:
    results = mock_searxng_search.invoke({"query":state["search_query"]})
    state["search_results"] = results
    print(f"\n[NODE 2] search results: {results}")
    return state

# --- node 3: draft the post ---
def draft_post(state:BotState)->BotState:
    persona = state["persona"]
    context = state["search_results"]
    topic = state["topic"]

    prompt = f"""You are this bot: {persona}

Today's topic: {topic}
Real-world context from search: {context}

Write a highly opinionated tweet (max 280 characters) in your voice.
Respond in JSON only, no markdown:
{{"bot_id": "{state['bot_id']}", "topic": "{topic}", "post_content": "..."}}"""

    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip()
    raw = raw.replace("```json","").replace("```","").strip()
    parsed = json.loads(raw)
    state["post_content"] = parsed["post_content"]
    print(f"\n[NODE 3] final post: {json.dumps(parsed, indent=2)}")
    return state

def build_graph():
    g = StateGraph(BotState)
    g.add_node("decide_search", decide_search)
    g.add_node("web_search", web_search)
    g.add_node("draft_post", draft_post)
    g.set_entry_point("decide_search")
    g.add_edge("decide_search","web_search")
    g.add_edge("web_search","draft_post")
    g.add_edge("draft_post", END)
    return g.compile()

def run_bot(bot_id:str):
    graph = build_graph()
    initial_state = BotState(
        bot_id=bot_id,
        persona=BOT_PERSONAS[bot_id],
        search_query="",
        search_results="",
        post_content="",
        topic="",
    )
    result = graph.invoke(initial_state)
    return {
        "bot_id": result["bot_id"],
        "topic": result["topic"],
        "post_content": result["post_content"],
    }

if __name__=="__main__":
    for bot_id in ["bot_a","bot_b","bot_c"]:
        print(f"\n{'='*50}")
        print(f"running {bot_id}...")
        output = run_bot(bot_id)
        print(f"\nfinal json output:")
        print(json.dumps(output, indent=2))
