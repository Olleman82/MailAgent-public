import base64
import email
import re
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

from googleapiclient.errors import HttpError

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.function_tool import FunctionTool

from auth.google_auth import get_gmail_service
from config import PROFILES


def _headers_map(headers: List[dict]) -> Dict[str, str]:
    return {h["name"]: h.get("value", "") for h in headers or []}


def _decode_body(payload: dict) -> Dict[str, str]:
    """Extract plain/text and html bodies from Gmail payload."""
    text_body = ""
    html_body = ""

    def walk(part: dict):
        nonlocal text_body, html_body
        mime = part.get("mimeType", "")
        data = part.get("body", {}).get("data")
        if data:
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            if mime == "text/plain":
                text_body += decoded
            elif mime == "text/html":
                html_body += decoded
        for sub in part.get("parts", []) or []:
            walk(sub)

    walk(payload)
    return {"text": text_body.strip(), "html": html_body.strip()}


def _normalize_internal_date(internal_date: Optional[str]) -> Optional[str]:
    if not internal_date:
        return None
    try:
        # Gmail returns ms since epoch as string.
        from datetime import datetime, timezone

        ts = datetime.fromtimestamp(int(internal_date) / 1000, tz=timezone.utc)
        return ts.isoformat()
    except Exception:
        return None


class GmailToolset(BaseToolset):
    """Wrap Gmail API actions for the agent."""

    def __init__(self):
        super().__init__()
        self._label_cache: Dict[str, str] = {}

    async def get_tools(self, readonly_context=None) -> List[BaseTool]:
        return [
            FunctionTool(self.gmail_list_unread),
            FunctionTool(self.gmail_get_thread),
            FunctionTool(self.gmail_find_related),
            FunctionTool(self.gmail_apply_label),
            FunctionTool(self.gmail_create_draft_reply),
            FunctionTool(self.gmail_search),
            FunctionTool(self.gmail_reply_draft_exists),
        ]

    def gmail_reply_draft_exists(self, thread_id: str, account: str = "default") -> bool:
        """Check if a draft already exists for this thread."""
        service = get_gmail_service(profile=account)
        drafts = (
            service.users()
            .drafts()
            .list(userId="me")
            .execute()
            .get("drafts", [])
        )
        for d in drafts:
            existing_thread = d.get("message", {}).get("threadId")
            if existing_thread == thread_id:
                return True
        return False

    def gmail_search(self, query: str, limit: int = 5, snippet_length: int = 100, profiles: List[str] = ["default", "private"]) -> List[Dict[str, Any]]:
        """
        Search for messages using Gmail query syntax (e.g. 'from:someone subject:waffles').
        Use a higher limit (e.g. 20-50) and short snippet_length to scan broadly.
        """
        items: List[Dict[str, Any]] = []
        
        # Filter available profiles
        valid_profiles = [p for p in profiles if p in PROFILES]
        
        for profile in valid_profiles:
            try:
                service = get_gmail_service(profile=profile)
                resp = (
                    service.users()
                    .messages()
                    .list(userId="me", q=query, maxResults=limit)
                    .execute()
                    or {}
                )
                
                for ref in resp.get("messages", []):
                    m = (
                        service.users()
                        .messages()
                        .get(
                            userId="me",
                            id=ref["id"],
                            format="metadata",
                            metadataHeaders=["From", "To", "Subject", "Date"],
                        )
                        .execute()
                    )
                    h = _headers_map(m.get("payload", {}).get("headers", []))
                    
                    snippet = m.get("snippet", "")
                    if len(snippet) > snippet_length:
                        snippet = snippet[:snippet_length] + "..."
                        
                    items.append(
                        {
                            "message_id": m.get("id"),
                            "thread_id": m.get("threadId"),
                            "from": h.get("From"),
                            "to": h.get("To"),
                            "subject": h.get("Subject"),
                            "date": h.get("Date"),
                            "snippet": snippet,
                            "account": profile  # Store which account this result is from
                        }
                    )
            except Exception as e:
                print(f"Error searching {profile}: {e}")
                
        return items

    def gmail_list_unread(self, limit: int = 10, account: str = "default") -> List[Dict[str, Any]]:
        """List unread messages with light metadata."""
        service = get_gmail_service(profile=account)
        resp = (
            service.users()
            .messages()
            .list(userId="me", q="is:unread", maxResults=limit)
            .execute()
            or {}
        )
        message_refs = resp.get("messages", [])
        items: List[Dict[str, Any]] = []
        for ref in message_refs:
            msg = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=ref["id"],
                    format="metadata",
                    metadataHeaders=["From", "To", "Subject", "Date"],
                )
                .execute()
            )
            headers = _headers_map(msg.get("payload", {}).get("headers", []))
            items.append(
                {
                    "message_id": msg.get("id"),
                    "thread_id": msg.get("threadId"),
                    "from": headers.get("From"),
                    "to": headers.get("To"),
                    "subject": headers.get("Subject"),
                    "snippet": msg.get("snippet"),
                    "internal_date": _normalize_internal_date(msg.get("internalDate")),
                    "account": account
                }
            )
        return items

    def gmail_get_thread(self, message_id: str, account: str = "default") -> Dict[str, Any]:
        """Fetch full thread for a message."""
        try:
            service = get_gmail_service(profile=account)
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
            headers = _headers_map(msg.get("payload", {}).get("headers", []))
            bodies = _decode_body(msg.get("payload", {}))
            thread_msgs: List[Dict[str, Any]] = []
            thread_id = msg.get("threadId")
            thread_resp = (
                service.users()
                .threads()
                .get(userId="me", id=thread_id, format="full")
                .execute()
            )
            for m in thread_resp.get("messages", []):
                th_headers = _headers_map(m.get("payload", {}).get("headers", []))
                th_bodies = _decode_body(m.get("payload", {}))
                thread_msgs.append(
                    {
                        "message_id": m.get("id"),
                        "snippet": m.get("snippet"),
                        "from": th_headers.get("From"),
                        "to": th_headers.get("To"),
                        "subject": th_headers.get("Subject"),
                        "date": th_headers.get("Date"),
                        "body": th_bodies,
                    }
                )

            return {
                "message_id": msg.get("id"),
                "thread_id": msg.get("threadId"),
                "headers": headers,
                "body": bodies,
                "thread": thread_msgs,
                "account": account
            }
        except HttpError as e:
            if e.resp.status == 404:
                return {"error": "Message or Thread not found", "message_id": message_id}
            raise e
        except Exception as e:
            return {"error": str(e), "message_id": message_id}

    def gmail_find_related(self, message_id: str, account: str = "default") -> List[Dict[str, Any]]:
        """Find mails in same thread or with similar subject across ALL context profiles."""
        service = get_gmail_service(profile=account)
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="metadata", metadataHeaders=["Subject"])
            .execute()
        )
        headers = _headers_map(msg.get("payload", {}).get("headers", []))
        subject = headers.get("Subject", "")
        cleaned = re.sub(r"^(re|fwd):\s*", "", subject, flags=re.IGNORECASE)
        query = f'subject:"{cleaned}"'
        return self.gmail_search(query=query, limit=10, profiles=["default", "private"])

    # Legacy method body is removed/replaced by above delegation
    def _ensure_label(self, service, label_name: str) -> str:
        """Return label id, creating it if needed."""
        if label_name in self._label_cache:
            return self._label_cache[label_name]

        existing = (
            service.users().labels().list(userId="me").execute().get("labels", [])
        )
        for lbl in existing:
            if lbl.get("name") == label_name:
                self._label_cache[label_name] = lbl["id"]
                return lbl["id"]

        body = {
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
            "name": label_name,
        }
        created = (
            service.users().labels().create(userId="me", body=body).execute()
        )
        self._label_cache[label_name] = created["id"]
        return created["id"]

    def gmail_apply_label(self, message_id: str, label_name: str, account: str = "default") -> Dict[str, Any]:
        """Create or reuse a label and apply it to a message."""
        service = get_gmail_service(profile=account)
        label_id = self._ensure_label(service, label_name)
        modified = (
            service.users()
            .messages()
            .modify(userId="me", id=message_id, body={"addLabelIds": [label_id]})
            .execute()
        )
        return {"message_id": message_id, "label": label_name, "result": modified}

    def gmail_create_draft_reply(self, message_id: str, reply_body: str, account: str = "default") -> Dict[str, Any]:
        """Create a Gmail draft reply for a given message."""
        service = get_gmail_service(profile=account)
        original = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="metadata", metadataHeaders=["From", "To", "Subject", "Message-ID"])
            .execute()
        )
        headers = _headers_map(original.get("payload", {}).get("headers", []))
        reply_to = headers.get("From")
        subject = headers.get("Subject", "")
        print(f"DEBUG: creating draft reply to='{reply_to}', subject='{subject}', original_id='{message_id}'")
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"

        # Clean and encode the 'To' header to avoid "Invalid To header" errors
        # with non-ASCII characters (e.g. "Olle Söderqvist")
        from email.utils import parseaddr, formataddr
        from email.header import Header
        
        name, addr = parseaddr(reply_to)
        encoded_name = str(Header(name, 'utf-8'))
        formatted_to = formataddr((encoded_name, addr))

        msg = MIMEText(reply_body)
        msg["To"] = formatted_to
        msg["Subject"] = subject
        if headers.get("Message-ID"):
            msg["In-Reply-To"] = headers["Message-ID"]
            msg["References"] = headers["Message-ID"]

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        draft = (
            service.users()
            .drafts()
            .create(
                userId="me",
                body={"message": {"raw": raw, "threadId": original.get("threadId")}},
            )
            .execute()
        )
        return {"draft_id": draft.get("id"), "thread_id": original.get("threadId")}
