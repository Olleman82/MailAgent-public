import asyncio
from typing import Dict, Any

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.function_tool import FunctionTool
from google.adk.runners import InMemoryRunner

from agents.context_agent import build_context_agent
from agents.radio_agent import build_radio_agent
from agents.calendar_agent import build_calendar_agent
from tools.google_search_toolset import GoogleSearchToolset


# Helper to run an agent single-shot
async def _run_agent_task(agent_builder, task_prompt: str, log_prefix: str) -> str:
    print(f"\n🤖 [Manager] Delegerar till {log_prefix}...")
    try:
        agent = agent_builder()
        runner = InMemoryRunner(agent=agent)
        # We run with quiet=True to keep main log clean, but you could enable it for debugging
        events = await runner.run_debug(task_prompt)
        
        # Determine the final answer. 
        # Collect all text from ModelResponse events, ignoring empty strings.
        # This ensures we get the final synthesis even if there were intermediate steps.
        final_text_parts = []
        used_tools = []
        
        for event in events:
            # Check for direct text attribute
            if hasattr(event, "text") and event.text:
                t = event.text.strip()
                if t:
                    final_text_parts.append(t)
            # Check for content.parts (common in ADK events)
            elif hasattr(event, "content") and event.content and hasattr(event.content, "parts"):
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        t = part.text.strip()
                        if t:
                            final_text_parts.append(t)
            
            if hasattr(event, "tool_calls") and event.tool_calls:
                for call in event.tool_calls:
                    used_tools.append(call.name)

        if used_tools:
            print(f"🛠️  [{log_prefix}] Verktyg som anropades: {', '.join(used_tools)}")

        # Use the last meaningful text chunk as the answer
        if final_text_parts:
            # We take the last one, as it's likely the summary after tool use.
            # Sometimes the agent thinks before speaking, so we might get thoughts.
            # Ideally we'd validte if it's a thought or user-msg, but for now:
            final_text = final_text_parts[-1]
        elif used_tools:
            # Fallback: Agent did work but didn't speak?
            final_text = f"Agenten utförde: {', '.join(used_tools)}, men gav ingen textrapport."
        else:
            final_text = "Ingen rapport."
        
        print(f"✅ [{log_prefix}] Svar: {final_text[:100]}...")
        return final_text
    except Exception as e:
        print(f"❌ [{log_prefix}] Misslyckades: {e}")
        return f"Delegering misslyckades: {str(e)}"


class DelegationToolset(BaseToolset):
    """
    Tools that allow the Main Agent to delegate tasks to Sub-Agents.
    """

    async def get_tools(self, readonly_context=None) -> list[BaseTool]:
        return [
            FunctionTool(self.ask_researcher),
            FunctionTool(self.ask_radio_expert),
            FunctionTool(self.ask_calendar_secretary),
            FunctionTool(self.ask_grounded_researcher),
        ]

    async def ask_researcher(self, query: str, email_context: str = "") -> str:
        """
        Delegera en sökning efter kontext/minnen till Research-agenten.
        Använd detta när du behöver veta vad som hänt tidigare (t.ex. "När var vi i London?", "Vad sa X om projektet?").
        Param: query - Beskriv vad du letar efter.
        Param: email_context - Hela texten från mailet som behandlas (för att ge agenten full kontext).
        """
        prompt = f"Uppdrag: Sök efter information om följande: '{query}'. Rapportera vad du hittar."
        if email_context:
            prompt += f"\n\nBAKGRUND (MAIL-KONTEXT):\n{email_context}"
        return await _run_agent_task(build_context_agent, prompt, "ResearchAgent")

    async def ask_radio_expert(self, query: str, email_context: str = "") -> str:
        """
        Delegera en fråga om Sveriges Radio (musik, program, nyheter) till Radio-experten.
        Använd detta när mailet handlar om radio, poddar eller musik.
        Param: query - Vad användaren vill ha (t.ex. "Krim-poddar", "Musik just nu", "Nyheter").
        Param: email_context - Hela texten från mailet som behandlas (för att ge agenten full kontext).
        """
        prompt = f"Uppdrag: Rekommendera innehåll baserat på önskemålet: '{query}'."
        if email_context:
            prompt += f"\n\nBAKGRUND (MAIL-KONTEXT):\n{email_context}"
        return await _run_agent_task(build_radio_agent, prompt, "RadioAgent")

    async def ask_calendar_secretary(self, request: str, email_context: str = "") -> str:
        """
        Delegera en bokning eller kalenderfråga till Kalender-sekreteraren.
        Använd detta för att boka möten eller kolla ledighet.
        Param: request - Detaljer om bokningen (t.ex. "Boka lunch imorgon 12:00").
        Param: email_context - Hela texten från mailet som behandlas (för att ge agenten full kontext).
        """
        prompt = f"Uppdrag: {request}. Kom ihåg att kolla krockar."
        if email_context:
            prompt += f"\n\nBAKGRUND (MAIL-KONTEXT):\n{email_context}"
        return await _run_agent_task(build_calendar_agent, prompt, "CalendarAgent")

    async def ask_grounded_researcher(self, query: str) -> str:
        """
        Delegera en kort grounded webbsökning när frågan är oklar eller kräver färska fakta.
        Param: query - Beskriv vad du behöver veta (t.ex. okänt namn/program).
        """
        prompt = (
            f"Gör en kort grounded webbsökning för att identifiera/förklara: '{query}'. "
            f"Ge kort sammanfattning och länkar."
        )
        # Kör verktyget direkt (Google Search toolset) för att undvika extra LLM-hopp
        try:
            toolset = GoogleSearchToolset()
            return await toolset.search_web(prompt)
        except Exception as e:
            return f"Grounded search misslyckades: {e}"
