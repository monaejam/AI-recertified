import os
import asyncio
from uuid import uuid4
from typing import Any, Optional

import httpx

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest


async def _send_a2a_message(query: str, base_url: str) -> str:
    """Send a single-turn message to the A2A server and return best-effort text.

    Falls back to returning the JSON payload if a clean text extraction isn't available.
    """
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()

        client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)

        payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": query}],
                "message_id": uuid4().hex,
            }
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**payload)
        )

        response = await client.send_message(request)

        # Try to extract any text parts from the structured response
        try:
            data = response.model_dump(mode="json", exclude_none=True)

            def _collect_text(obj: Any) -> list[str]:
                texts: list[str] = []
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if k == "text" and isinstance(v, str):
                            texts.append(v)
                        else:
                            texts.extend(_collect_text(v))
                elif isinstance(obj, list):
                    for item in obj:
                        texts.extend(_collect_text(item))
                return texts

            texts = _collect_text(data)
            if texts:
                return "\n".join(texts)
            return response.model_dump_json(indent=2, exclude_none=True)
        except Exception:
            return "Received response from A2A server, but could not parse content."


@tool
async def call_a2a_agent(
    query: str, base_url: Optional[str] = None
) -> str:
    """Delegate the user's query to the internal A2A agent server and return its answer.

    - If base_url is not provided, uses A2A_BASE_URL env var or http://localhost:10000
    """
    base = base_url or os.getenv("A2A_BASE_URL", "http://localhost:10000")
    return await _send_a2a_message(query=query, base_url=base)


def build_simple_a2a_client_agent():
    """Build a minimal ReAct agent that always delegates via the A2A tool."""
    model = ChatOpenAI(
        model=os.getenv("TOOL_LLM_NAME", "gpt-4o-mini"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("TOOL_LLM_URL", "https://api.openai.com/v1"),
        temperature=0,
    )
    tools = [call_a2a_agent]
    graph = create_react_agent(model, tools)
    return graph


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Simple LangGraph agent using A2A")
    parser.add_argument("query", nargs="*", help="User query to answer via A2A")
    parser.add_argument(
        "--base-url",
        default=os.getenv("A2A_BASE_URL", "http://localhost:10000"),
        help="Base URL of the A2A server",
    )
    args = parser.parse_args()

    user_query = " ".join(args.query).strip() or "What can you do?"

    # If no OpenAI key is present, skip building a local LLM agent and
    # directly delegate to the A2A server.
    if not os.getenv("OPENAI_API_KEY"):
        text = await _send_a2a_message(user_query, args.base_url)
        print(text)
        return

    graph = build_simple_a2a_client_agent()

    inputs = {
        "messages": [
            (
                "system",
                "Always delegate to the call_a2a_agent tool to answer the user's query.",
            ),
            ("user", user_query),
        ]
    }

    # Run a single turn and print the agent's final message content
    result = graph.invoke(inputs)
    try:
        message = result["messages"][-1]
        content = getattr(message, "content", str(message))
        print(content)
    except Exception:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())


