# simple_langgraph_app.py
import asyncio
import os
from dotenv import load_dotenv

# MCP (client) bits
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Turn MCP tools into LangChain Tools
from langchain_mcp_adapters.tools import load_mcp_tools

# LLM + Agent
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage

load_dotenv()

# --- Path to  MCP server.py ---
SERVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "server.py"))

# Toggle: let the agent perform tool calls, or do them deterministically here
USE_AGENT_FOR_CALLS = True   # <— flipped this on

async def main():
    # 1) Start  MCP server over stdio
    server_params = StdioServerParameters(
        command="python",
        args=[SERVER_PATH],
        env=os.environ.copy(),   # so the server can read TAVILY_API_KEY, etc.
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 2) Load MCP tools as LangChain tools
            tools = await load_mcp_tools(session)
            print("Loaded MCP tools:", [t.name for t in tools])  # ['web_search','roll_dice','fetch_title']
            tool_map = {t.name: t for t in tools}

            # 3) LLM + agent
            llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
            agent = create_react_agent(llm, tools)  # ← no state_modifier here on new langgraph

            if USE_AGENT_FOR_CALLS:
                # --- Agent performs the tool calls (guardrail via SystemMessage) ---
                guardrail = SystemMessage(
                    content=(
                        "When the user specifies a URL, you MUST pass that exact URL to the "
                        "'fetch_title' tool without replacing or normalizing it."
                    )
                )
                user_prompt = (
                    "1) Fetch the title of https://github.com\n"
                    "2) Roll 2d6\n"
                    "3) Search the web for 'LangGraph MCP adapter quickstart'\n"
                    "Return all results clearly."
                )
                result = await agent.ainvoke(
                    {"messages": [guardrail, {"role": "user", "content": user_prompt}]}
                )
                final_msg = result["messages"][-1].content
                print("\n=== Agent Response ===\n", final_msg)

            else:
                # --- Deterministic tool calls (no drift) ---
                url = "https://github.com"
                dice_notation = "2d6"
                query = "LangGraph MCP adapter quickstart"

                title = await tool_map["fetch_title"].ainvoke({"url": url})
                dice = await tool_map["roll_dice"].ainvoke({"notation": dice_notation, "num_rolls": 1})
                search = await tool_map["web_search"].ainvoke({"query": query})

                # Ask the LLM only to format, not to make tool calls
                summary_prompt = (
                    f"Summarize these tool results clearly:\n\n"
                    f"1) fetch_title({url}) -> {title}\n"
                    f"2) roll_dice({dice_notation}) -> {dice}\n"
                    f"3) web_search({query}) -> {search}\n"
                )
                formatted = await llm.ainvoke(summary_prompt)

                print("\n=== Deterministic Results (raw) ===")
                print("Title:", title)
                print("Dice: ", dice)
                if isinstance(search, str) and len(search) > 800:
                    print("Search:", search[:800] + "…")
                else:
                    print("Search:", search)

                print("\n=== Neatly Formatted ===\n", getattr(formatted, "content", str(formatted)))

if __name__ == "__main__":
    asyncio.run(main())
