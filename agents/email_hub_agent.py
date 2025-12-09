from google.adk.agents.llm_agent import LlmAgent
from google.adk.models import Gemini
from google.adk.tools.google_search_tool import google_search
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL
from tools.calendar_tools import CalendarToolset
from tools.gmail_tools import GmailToolset
from tools.sr_mcp_tools import SrMcpToolset


def build_email_hub_agent() -> LlmAgent:
    """Create the root ADK agent with Gmail + Calendar tools."""
from pathlib import Path
from config import BASE_DIR, GEMINI_API_KEY, GEMINI_MODEL

# ... existing imports ...

def build_email_hub_agent() -> LlmAgent:
    """Create the root ADK agent with Gmail + Calendar tools."""
    
    # Load instructions from external file
    # Priority: agent_instruction.txt (Private) -> agent_instruction.default.txt (Public)
    instruction_file = BASE_DIR / "agent_instruction.txt"
    if not instruction_file.exists():
        instruction_file = BASE_DIR / "agent_instruction.default.txt"
    
    try:
        instruction = instruction_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"⚠️ Could not load instruction file: {e}")
        instruction = "You are a helpful mail assistant."

    model = Gemini(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)

    generate_cfg = types.GenerateContentConfig(
        temperature=0.2,
    )

    # Tools: gmail, calendar, web search.
    tools = [
        GmailToolset(),
        CalendarToolset(),
        SrMcpToolset(),
        # google_search,
    ]

    agent = LlmAgent(
        name="email_hub_agent",
        model=model,
        instruction=instruction.strip(),
        tools=tools,
        generate_content_config=generate_cfg,
    )

    return agent
