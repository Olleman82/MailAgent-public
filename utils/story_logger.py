import json

def print_story_event(event):
    """
    Pedagogical logger that converts raw agent events into a user-friendly story.
    Handles 'Thinking', 'Tool Calls' (Searching), and 'Model Responses'.
    """
    
    # 1. Handle Thinking (Requires the model to be configured with thinking_config)
    # The structure can vary, but often appears in candidates.content.parts
    if hasattr(event, "content") and event.content:
        # Check for candidates (Gemini)
        # Sometimes event is a GenerateContentResponse or a simpler wrapper
        # We try to find 'parts'
        parts = []
        if hasattr(event.content, 'parts'):
            parts = event.content.parts
        
        for part in parts:
            # Check for thought parts (experimental feature)
            if hasattr(part, "thought") and part.thought:
                # Hantera endast str; undvik krasch om 'thought' råkar vara bool/annat
                if isinstance(part.thought, str):
                    print(f"\n🧠 \033[95mTÄNKER:\033[0m")
                    print(f"  \"{part.thought.strip()}\"")
                else:
                    continue
            elif hasattr(part, "text") and part.text:
                 # Sometimes thoughts are leaked in text if not parsed correctly, 
                 # but usually text is the final response. We handle text below.
                 pass

    # 2. Handle Tool Calls (Searching, Reading)
    # The ADK event wrapper usually has 'tool_calls' if it's a request
    if hasattr(event, "tool_calls") and event.tool_calls:
        for call in event.tool_calls:
            # Extract function name and properly formatted args
            fname = call.name
            args =  {k: v for k, v in call.args.items()}
            
            if fname == "gmail_search":
                q = args.get("query", "???")
                p = args.get("profiles", ["default"])
                print(f"\n🔎 \033[94mSÖKER:\033[0m \"{q}\" i {p}...")
            
            elif fname == "gmail_get_thread":
                mid = args.get("message_id", "???")
                print(f"\n👁️ \033[94mLÄSER:\033[0m Hämtar hela konversationen för mail-ID {mid} (djupdykning)...")
                
            elif fname == "gmail_create_draft_reply":
                print(f"\n✍️ \033[92mSKRIVER:\033[0m Skapar utkast på svar...")

            elif fname == "calendar_create_event":
                summary = args.get("summary", "???")
                print(f"\n📅 \033[92mKALENDER:\033[0m Bokar \"{summary}\"...")
            
            # SR MCP Tools
            elif fname in ["search_programs", "search_episodes", "search_all"]:
                q = args.get("query", "???")
                print(f"\n📻 \033[96mRADIO (SÖK):\033[0m Letar efter program om \"{q}\"...")
            
            elif fname in ["get_channel_rightnow", "get_all_rightnow"]:
                print(f"\n📻 \033[96mRADIO (NU):\033[0m Kollar vad som sänds just nu...")

            elif fname.startswith("get_") and "program" in fname:
                 print(f"\n📻 \033[96mRADIO (INFO):\033[0m Hämtar detaljer om ett program...")

            else:
                print(f"\n🔧 \033[90mVERKTYG:\033[0m Använder {fname} {args}")

    # 3. Handle Tool Outputs (Results)
    # ADK typically sends a separate event for tool output
    if hasattr(event, "tool_response") and event.tool_response:
        tr = event.tool_response
        fname = tr.name
        content = tr.output
        
        if fname == "gmail_search":
            # Count items
            try:
                # Content is often a dict `{'result': [...]}` or just the list
                items = []
                if isinstance(content, dict) and 'result' in content:
                    items = content['result']
                elif isinstance(content, list):
                    items = content
                
                count = len(items)
                if count == 0:
                    print(f"  ❌ Hittade inga träffar.")
                else:
                    print(f"  📄 Hittade {count} mail. (Inspekterar metadatat...)")
                    # Show top 3 subjects
                    for i, item in enumerate(items[:3]):
                            subj = item.get("subject", "No Subject")
                            print(f"    - {subj}")
                    if count > 3:
                        print(f"    ...och {count-3} till.")
            except:
                print(f"  ✅ Sökning klar.")

    # 4. Handle Final Model Response
    if hasattr(event, "content") and event.content:
        # Check if this is a final response (no tool calls pending)
        is_tool_call = hasattr(event, "tool_calls") and event.tool_calls
        if not is_tool_call and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    # Avoid printing if it's just a small function call artifact
                    if len(part.text) > 5:
                        print(f"\n💬 \033[96mSVAR:\033[0m {part.text.strip()}\n")
