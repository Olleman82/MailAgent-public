import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models import Gemini
from google.genai import types

from config import BASE_DIR, GEMINI_API_KEY, GEMINI_MODEL
from tools.google_search_toolset import GoogleSearchToolset


def build_grounding_agent() -> LlmAgent:
    """
    Grounded web-research agent using Google Search grounding.
    """

    # Inject current date
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    instruction_prefix = f"IDAG ÄR DET: {today_str}.\n\n"

    instruction_file = BASE_DIR / "grounding_instruction.txt"
    try:
        if instruction_file.exists():
            file_content = instruction_file.read_text(encoding="utf-8").strip()
        else:
            file_content = (BASE_DIR / "grounding_instruction.default.txt").read_text(encoding="utf-8").strip()
        instruction = instruction_prefix + file_content
    except Exception as e:
        print(f"⚠️ Could not load grounding instruction file: {e}")
        instruction = instruction_prefix + "Gör kort webbresearch med Google-grounding, länka källor och håll det kort."

    if not GEMINI_API_KEY:
        # Explicit guard so felrapporten blir tydlig när nyckeln saknas.
        raise RuntimeError("GEMINI_API_KEY saknas, grounding-agenten kan inte köras.")

    # Säkerställ att vi kör mot API-nyckeln (ej Vertex) för grounded sök
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"

    model = Gemini(api_key=GEMINI_API_KEY, model="gemini-flash-latest")

    generate_cfg = types.GenerateContentConfig(
        temperature=0.3,
    )

    agent = LlmAgent(
        name="grounded_web_researcher",
        model=model,
        instruction=instruction,
        tools=[GoogleSearchToolset()],
        generate_content_config=generate_cfg,
    )

    return agent

