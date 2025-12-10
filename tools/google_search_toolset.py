import asyncio
import aiohttp
from typing import Optional

from google import genai
from google.genai import types
from google.genai import errors as genai_errors

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.function_tool import FunctionTool

from config import GEMINI_API_KEY, GEMINI_MODEL

# ADK monkeypatch (samma som i main.py) för att undvika aiohttp-attributfel
if not hasattr(aiohttp, "ClientConnectorDNSError"):
    aiohttp.ClientConnectorDNSError = aiohttp.ClientConnectorError


async def _do_search(query: str) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    try:
        resp = await asyncio.to_thread(
            client.models.generate_content,
            model=GEMINI_MODEL,
            contents=query,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )
        # Extract text and grounding info if available
        text = resp.text or ""
        sources = []
        try:
            meta = resp.candidates[0].grounding_metadata
            if meta and meta.grounding_chunks:
                for ch in meta.grounding_chunks:
                    if getattr(ch, "web", None) and getattr(ch.web, "title", None):
                        sources.append(ch.web.title)
        except Exception:
            pass
        if sources:
            return f"{text}\n\nKällor: " + "; ".join(sources)
        return text
    except genai_errors.ClientError as e:
        return f"Grounded sökning misslyckades (ClientError): {e}"
    except Exception as e:
        return f"Grounded sökning misslyckades: {e}"


class GoogleSearchToolset(BaseToolset):
    """
    Exponerar ett enkelt grounded web-sök via Google Search tool.
    """

    async def get_tools(self, readonly_context=None) -> list[BaseTool]:
        return [FunctionTool(self.search_web)]

    async def search_web(self, query: str) -> str:
        """
        Kör ett grounded webbsök (Google Search tool) och returnerar text + källor.
        """
        return await _do_search(query)

