from google.adk.agents.llm_agent import LlmAgent
from google.adk.models import Gemini
from google.genai import types
from google.adk.planners import BuiltInPlanner

from config import BASE_DIR, GEMINI_API_KEY, GEMINI_MODEL

# NEW: Import only the DelegationToolset. 
# The specialized tools are now hidden inside the sub-agents.
from tools.delegation_tools import DelegationToolset


def build_email_hub_agent() -> LlmAgent:
    """
    Create the root ADK agent (THE MANAGER).
    It uses DelegationTools to dispatch tasks to:
    - ContextAgent (Research)
    - RadioAgent (Entertainment)
    - CalendarAgent (Booking)
    """
    
    # Load instructions from external file
    # Priority: agent_instruction.txt (Private) -> agent_instruction.default.txt (Public)
    # Inject current date for accurate time awareness
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    instruction_text = f"IDAG ÄR DET: {today_str}.\n\n"

    try:
        instruction_file = BASE_DIR / "agent_instruction.txt"
        if not instruction_file.exists():
            instruction_file = BASE_DIR / "agent_instruction.default.txt"
        
        file_content = instruction_file.read_text(encoding="utf-8")
        instruction = instruction_text + file_content
    except Exception as e:
        print(f"⚠️ Could not load instruction file: {e}")
        instruction = instruction_text + "You are a helpful mail assistant manager."

    model = Gemini(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)

    generate_cfg = types.GenerateContentConfig(
        temperature=0.2, # Low temp for the manager to follow rules strictly
    )

    # Tools: ONLY Delegation + Maybe simple Gmail tools for JUST listing the inbox?
    # Actually, the 'main.py' uses this agent to PROCESS emails. 
    # The main loop fetches the email content and puts it in the prompt.
    # So the agent technically doesn't need to read separate emails unless it wants to search history.
    # But wait, in 'main.py' distinct categorization happens.
    
    # However, for creating drafts, we might still want the main agent to do it? 
    # OR should we have a 'ResponderAgent'?
    # For now, let's keep 'GmailToolset' only for 'create_draft' and 'apply_label' in the main agent?
    # NO, strictly following the hierarchy: The main agent decides WHAT to do.
    # Creating a draft is simple enough to stay in the main agent OR be a tool.
    # Let's keep the write-tools in the main agent for now to avoid over-engineering the response part.
    # The user asked for "Work distributor".
    
    # Let's import GmailToolset but ONLY give it write-access? 
    # The current GmailToolset is a bundle.
    # Let's include GmailToolset for basic labeled/drafting, but rely on Delegation for the heavy lifting.
    
    from tools.gmail_tools import GmailToolset
    
    tools = [
        DelegationToolset(), # The new superpowers
        GmailToolset(),      # Needs this to label "AI-Processed" and create drafts
    ]

    planner = BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            thinking_budget=4000,
            include_thoughts=True,
        )
    )

    agent = LlmAgent(
        name="email_hub_manager",
        model=model,
        instruction=instruction.strip(),
        tools=tools,
        generate_content_config=generate_cfg,
        planner=planner,
    )

    return agent
