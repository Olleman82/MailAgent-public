import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from a local .env file if present.
# override=True ensures .env takes priority over system environment variables.
load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent

# OAuth files (desktop app credentials).
CREDENTIALS_FILE = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", BASE_DIR / "credentials.json"))
# OAuth files (desktop app credentials).
import json

# OAuth files (desktop app credentials).
CREDENTIALS_FILE = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", BASE_DIR / "credentials.json"))

# Load profiles from external JSON or env, otherwise default
PROFILES_FILE = BASE_DIR / "profiles.json"
if PROFILES_FILE.exists():
    try:
        data = json.loads(PROFILES_FILE.read_text(encoding="utf-8"))
        # Convert values to Path objects
        PROFILES = {k: Path(v) for k, v in data.items()}
    except Exception as e:
        print(f"⚠️ Error loading profiles.json: {e}, using default.")
        PROFILES = {"default": Path("token.json")}
else:
    # Default public config
    PROFILES = {
        "default": Path(BASE_DIR / "token.json")
    }

# Backwards compatibility accessor (points to default)
TOKEN_FILE = PROFILES["default"]

# Combined scopes so Gmail/Calendar share the same token.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]

# Gemini model + API key.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Default batch size for triage.
DEFAULT_UNREAD_LIMIT = int(os.getenv("UNREAD_LIMIT", "10"))

# User-friendly app name for OAuth consent screen.
APP_NAME = os.getenv("APP_NAME", "Mail & Calendar Copilot (Lab)")
