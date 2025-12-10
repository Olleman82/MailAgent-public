from google.adk.agents.llm_agent import LlmAgent
from google.adk.models import Gemini
from google.genai import types
from google.adk.planners import BuiltInPlanner

from config import BASE_DIR, GEMINI_API_KEY, GEMINI_MODEL
from tools.calendar_tools import CalendarToolset


def build_calendar_agent() -> LlmAgent:
    """
    Creates the Calendar/Booking Specialist Agent.
    Role: Check availability and book events.
    """
    
    # Inject current date
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    instruction_prefix = f"IDAG ÄR DET: {today_str}.\n\n"

    instruction_file = BASE_DIR / "calendar_instruction.txt"
    try:
        if instruction_file.exists():
            file_content = instruction_file.read_text(encoding="utf-8").strip()
        else:
            file_content = (BASE_DIR / "calendar_instruction.default.txt").read_text(encoding="utf-8").strip()
        instruction = instruction_prefix + file_content
    except Exception as e:
        print(f"⚠️ Could not load calendar instruction file: {e}")
        instruction = instruction_prefix + "Du hanterar bokningar, kollar krockar och bokar bara i familjekalendern."

    model = Gemini(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)

    generate_cfg = types.GenerateContentConfig(
        temperature=0.1, # Very deterministic for booking
    )

    tools = [
        CalendarToolset(),
    ]

    planner = BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            thinking_budget=4000,
            include_thoughts=True,
        )
    )

    agent = LlmAgent(
        name="calendar_secretary",
        model=model,
        instruction=instruction,
        tools=tools,
        generate_content_config=generate_cfg,
        planner=planner,
    )

    return agent
