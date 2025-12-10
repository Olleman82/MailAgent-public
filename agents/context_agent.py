from google.adk.agents.llm_agent import LlmAgent
from google.adk.models import Gemini
from google.genai import types
from google.adk.planners import BuiltInPlanner

from config import BASE_DIR, GEMINI_API_KEY, GEMINI_MODEL
from tools.gmail_tools import GmailToolset


def build_context_agent() -> LlmAgent:
    """
    Creates the Research Specialist Agent.
    Role: Search 'private' profile for long-term context/memories.
    """
    
    # Inject current date
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    instruction_prefix = f"IDAG ÄR DET: {today_str}.\n\n"

    instruction_file = BASE_DIR / "context_instruction.txt"
    try:
        if instruction_file.exists():
            file_content = instruction_file.read_text(encoding="utf-8").strip()
        else:
            file_content = (BASE_DIR / "context_instruction.default.txt").read_text(encoding="utf-8").strip()
        instruction = instruction_prefix + file_content
    except Exception as e:
        print(f"⚠️ Could not load context instruction file: {e}")
        instruction = instruction_prefix + "Sök i 'private'-profilen efter historik och rapportera exakt vad du hittar."

    model = Gemini(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)

    # Use thinking for complex search strategies
    generate_cfg = types.GenerateContentConfig(
        temperature=0.2,
    )

    tools = [
        GmailToolset(),
    ]

    planner = BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            thinking_budget=12000,
            include_thoughts=True,
        )
    )

    agent = LlmAgent(
        name="concept_researcher",
        model=model,
        instruction=instruction,
        tools=tools,
        generate_content_config=generate_cfg,
        planner=planner,
    )

    return agent
