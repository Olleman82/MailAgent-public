# Mail & Calendar Copilot (Google ADK)

A powerful, agentic AI assistant for Gmail and Google Calendar. It uses Google's Agent Development Kit (ADK) and Gemini Pro to intelligently triage emails, draft replies, and manage calendar events.

**Key Features:**
*   **Intelligent Triage:** Categorizes emails (Reply, To-Do, Info) and applies Gmail labels.
*   **Smart Replies:** Drafts context-aware replies based on email history and thread context.
*   **Calendar Management:** Automatically detects event invites and checks your calendar for conflicts before suggesting bookings.
*   **Thinking Agent:** Uses "thinking" capabilities to reason about complex requests before acting.
*   **External Tool Support:** (Optional) Support for Model Context Protocol (MCP) tools, e.g., Sveriges Radio search.

## 🚀 Getting Started

### Prerequisites
1.  **Python 3.10+**
2.  **Google Cloud Project** with Gmail API and Calendar API enabled.
3.  **Gemini API Key** from Google AI Studio.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/mail-cal-copilot.git
    cd mail-cal-copilot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Configuration:**
    *   Create a `.env` file based on `.env.example` (if provided) or manually:
        ```bash
        GEMINI_API_KEY=your_api_key_here
        GEMINI_MODEL=gemini-2.5-flash
        ```

4.  **Google Authentication:**
    *   Place your desktop OAuth client secrets file as `credentials.json` in the root folder.
    *   Run the agent once to authenticate via browser: `python main.py`.

### Customization

#### 1. Agent Instructions (Prompt)
The agent comes with a generic default prompt in `agent_instruction.default.txt`.
To customize the agent's persona and rules for **YOUR** needs:
1.  Copy `agent_instruction.default.txt` to `agent_instruction.txt`.
2.  Edit `agent_instruction.txt` with your specific instructions (e.g., "You are helpful...", "Always sign as Bob", etc.).
    *   *Note: `agent_instruction.txt` is gitignored so your personal prompt stays private.*

#### 2. Multiple Accounts (Optional)
If you want the agent to access multiple Gmail/Calendar accounts (e.g., Personal, Work, Family):
1.  Create a file named `profiles.json` in the root directory.
2.  Define your profile mappings:
    ```json
    {
        "default": "token.json",
        "work": "token_work.json",
        "family": "token_family.json"
    }
    ```
3.  The agent can now be instructed to search in specific profiles (e.g., `profiles=['work']`).
    *   *Note: `profiles.json` is gitignored.*

## 🏃 Usage

**Run a one-time triage of your last 10 emails:**
```bash
python main.py --limit 10
```

**Run in Watchdog Mode (Continuous):**
Checks for new emails every minute and wakes up only when needed.
```bash
python main.py --watch --interval 60
```
