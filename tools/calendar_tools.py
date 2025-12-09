from typing import Dict

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.function_tool import FunctionTool

from auth.google_auth import get_calendar_service


class CalendarToolset(BaseToolset):
    """Calendar helpers for the agent."""

    async def get_tools(self, readonly_context=None) -> list[BaseTool]:
        return [
            FunctionTool(self.calendar_create_event),
            FunctionTool(self.calendar_list_events),
        ]

    def calendar_list_events(
        self, time_min: str, time_max: str, max_results: int = 10, profiles: list[str] = ["default", "family"]
    ) -> list[Dict[str, str]]:
        """List events on primary calendar between time_min and time_max (RFC3339)."""
        all_events = []
        for profile in profiles:
            try:
                service = get_calendar_service(profile=profile)
                events_result = (
                    service.events()
                    .list(
                        calendarId="primary",
                        timeMin=time_min,
                        timeMax=time_max,
                        maxResults=max_results,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )
                items = events_result.get("items", [])
                for e in items:
                    all_events.append({
                        "id": e.get("id"),
                        "summary": f"[{profile}] {e.get('summary', '')}",
                        "start": e.get("start", {}).get("dateTime", e.get("start", {}).get("date")),
                        "end": e.get("end", {}).get("dateTime", e.get("end", {}).get("date")),
                        "profile": profile
                    })
            except Exception as e:
                print(f"Error fetching calendar for {profile}: {e}")
        
        # Sort combined list by start time
        all_events.sort(key=lambda x: x.get("start", ""))
        return all_events[:max_results]

    def calendar_create_event(
        self,
        summary: str,
        start_iso: str,
        end_iso: str,
        description: str = "",
        message_id: str | None = None,
        timezone: str | None = None,
    ) -> Dict[str, str]:
        """
        Create a calendar event on the FAMILY calendar (default).

        start_iso/end_iso should be RFC3339 timestamps with timezone info when possible.
        If message_id is provided, a Gmail-länk läggs till i description.
        """
        service = get_calendar_service(profile="family")

        desc = description or ""
        if message_id:
            gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{message_id}"
            if desc:
                desc += "\n\n"
            desc += f"Gmail: {gmail_link}"

        # Default to 'Europe/Stockholm' if no timezone is provided, to avoid "Missing time zone" errors
        tz = timezone or "Europe/Stockholm"
        
        event_body: Dict[str, dict | str] = {
            "summary": summary,
            "description": desc,
            "start": {"dateTime": start_iso, "timeZone": tz},
            "end": {"dateTime": end_iso, "timeZone": tz},
        }

        created = (
            service.events()
            .insert(calendarId="primary", body=event_body, sendUpdates="none")
            .execute()
        )
        return {"event_id": created.get("id"), "htmlLink": created.get("htmlLink", "")}
