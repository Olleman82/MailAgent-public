import argparse
import asyncio
import json
import sys
from pathlib import Path

# Monkeypatch aiohttp to fix google-genai crash on retry
import aiohttp
if not hasattr(aiohttp, "ClientConnectorDNSError"):
    aiohttp.ClientConnectorDNSError = aiohttp.ClientConnectorError


from google.adk.runners import InMemoryRunner
from google.genai import types

from agents.email_hub_agent import build_email_hub_agent
import time
from auth.google_auth import get_gmail_service, describe_auth_state
from config import DEFAULT_UNREAD_LIMIT

def check_unread_count(profile: str = "default") -> int:
    """Check if there are unread messages without fetching content."""
    try:
        service = get_gmail_service(profile=profile)
        results = service.users().messages().list(
            userId="me", q="label:UNREAD -label:AI-Processed", maxResults=1
        ).execute()
        return len(results.get("messages", []))
    except Exception as e:
        print(f"Watchdog Error during check: {e}")
        return 0

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Mail & Calendar co-pilot (Google ADK)."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_UNREAD_LIMIT,
        help="Antal olästa mail att triagera (default från env UNREAD_LIMIT eller 10).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Skriv bara slutlig summering (behåll event-logik tyst).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skicka ingen ny prompt till modellen, bara visa auth-läge.",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Kör i Watchdog-läge (loopande övervakning).",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Sekunder att vänta mellan sökningar i Watchdog-läge (default 60s).",
    )
    return parser.parse_args()


from utils.story_logger import print_story_event

async def run_triage(limit: int, quiet: bool) -> None:
    # ... existing run_triage code ...
    agent = build_email_hub_agent()
    runner = InMemoryRunner(agent=agent, app_name="mail_calendar_copilot")

    prompt = (
        f"Triagera mina senaste {limit} olästa mail som INTE har etiketten 'AI-Processed'. "
        "För varje mail: \n"
        "1. Bestäm kategori (Svara/Barnens/Övrigt).\n"
        "2. Sätt etiketten 'AI-Processed' PÅ ALLA som är behandlade (för att undvika loopar).\n"
        "3. Skapa ev. utkast/kalenderhändelse.\n"
        "4. Sammanfatta."
    )

    print(f"🚀 Startar triage av {limit} mail med Thinking-agent...\n")
    
    # Use run_debug to avoid manual session management issues, but collect events
    events = await runner.run_debug(prompt, quiet=True) 

    # Log events to story logger
    print("\n--- 📝 Agentens Resonemang & Åtgärder ---")
    
    # Store all tool calls to check if SR tools were used
    sr_tools_used = False
    
    for event in events:
        print_story_event(event)
        
        # Check if any SR tool was called
        if hasattr(event, "tool_calls") and event.tool_calls:
            for call in event.tool_calls:
                if call.name in ["search_programs", "get_channel_rightnow", "get_all_rightnow", "list_channels"]:
                    sr_tools_used = True
    
    if not sr_tools_used:
        # Only warn if it looks like we missed an opportunity? 
        # Actually this warning writes every time, maybe we should suppress it if no relevant email was found?
        # But for now, let's keep it or remove it. The user wanted debug.
        # Let's keep it simple.
        pass
    
    print("\n✅ Triage slutförd.")


def main() -> None:
    args = parse_args()

    if args.dry_run:
        print("Auth-läge:")
        print(json.dumps(describe_auth_state(), indent=2))
        sys.exit(0)

    if args.watch:
        print(f"🐕 Startar Watchdog-läge. Kollar mail var {args.interval} sekund...")
        try:
            while True:
                # 1. Check if unread mail exists (cheap check)
                count = check_unread_count("default")
                if count > 0:
                    print(f"\n📨 Hittade {count}+ olästa mail! Väckte agenten...")
                    try:
                        asyncio.run(run_triage(args.limit, args.quiet))
                    except Exception as e:
                        print(f"❌ Fel under triage-körning: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    # Optional: Print dot to show aliveness
                    # print(".", end="", flush=True) 
                    pass

                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n🛑 Watchdog stoppad av användare.")
            sys.exit(0)
    else:
        # Normal one-off run
        try:
            asyncio.run(run_triage(args.limit, args.quiet))
            print("Triage completed successfully.")
        except Exception:
            import traceback
            traceback.print_exc()



if __name__ == "__main__":
    main()
