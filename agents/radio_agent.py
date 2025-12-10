from google.adk.agents.llm_agent import LlmAgent
from google.adk.models import Gemini
from google.genai import types

from config import BASE_DIR, GEMINI_API_KEY, GEMINI_MODEL
from tools.sr_mcp_tools import SrMcpToolset

from google.adk.planners import BuiltInPlanner


def build_radio_agent() -> LlmAgent:
    """
    Creates the Radio/Entertainment Specialist Agent.
    Role: Interface with Sveriges Radio MCP.
    """
    
    # Inject current date
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    instruction_prefix = f"IDAG ÄR DET: {today_str}.\n\n"

    instruction_file = BASE_DIR / "radio_instruction.txt"
    try:
        if instruction_file.exists():
             file_content = instruction_file.read_text(encoding="utf-8").strip()
        else:
             file_content = (BASE_DIR / "radio_instruction.default.txt").read_text(encoding="utf-8").strip()
        instruction = instruction_prefix + file_content
    except Exception as e:
        print(f"⚠️ Could not load radio instruction file: {e}")
        instruction = instruction_prefix + "Hitta SR-program via verktygen, gissa aldrig, lista med namn, beskrivning, kanal och länk."

    model = Gemini(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)

    generate_cfg = types.GenerateContentConfig(
        temperature=0.4, # Slightly higher for creativity in recommendations
    )

    tools = [
        SrMcpToolset(),
    ]

    # Planner with explicit thinking budget using google.genai.types.ThinkingConfig
    planner = BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            thinking_budget=8000,
            include_thoughts=True,
        )
    )

    agent = LlmAgent(
        name="radio_expert",
        model=model,
        instruction=instruction,
        tools=tools,
        generate_content_config=generate_cfg,
        planner=planner,
    )

    return agent
