import json
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import APP_NAME, CREDENTIALS_FILE, PROFILES, SCOPES, TOKEN_FILE


def _load_saved_token(token_file: Path) -> Optional[Credentials]:
    if not token_file.exists():
        return None
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def _persist_token(creds: Credentials, token_file: Path) -> None:
    token_file.write_text(creds.to_json(), encoding="utf-8")


def _run_oauth_flow(creds_file: Path) -> Credentials:
    flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
    # Desktop app flow will open a browser window on first run.
    return flow.run_local_server(port=0)


def _get_credentials(profile: str = "default") -> Credentials:
    token_path = PROFILES.get(profile, PROFILES["default"])

    creds = _load_saved_token(token_path)
    if creds and creds.valid:
        return creds

    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            f"credentials.json saknas. Lägg den i {CREDENTIALS_FILE} och kör igen."
        )

    print(f"--- Authenticating profile: {profile} ---")
    creds = _run_oauth_flow(CREDENTIALS_FILE)
    _persist_token(creds, token_path)
    return creds


def get_gmail_service(profile: str = "default"):
    """Return a Gmail API client with modify scope."""
    creds = _get_credentials(profile)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def get_calendar_service(profile: str = "default"):
    """Return a Google Calendar API client."""
    creds = _get_credentials(profile)
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def describe_auth_state() -> dict:
    """Small helper for debugging auth status."""
    return {
        "token_file_exists": TOKEN_FILE.exists(),
        "credentials_file_exists": CREDENTIALS_FILE.exists(),
        "token_path": str(TOKEN_FILE),
        "credentials_path": str(CREDENTIALS_FILE),
        "scopes": SCOPES,
        "app_name": APP_NAME,
    }
