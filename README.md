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

### 🔑 Google Cloud & Authentication Setup

To allow the agent to access your email and calendar, you need to set up a Google Cloud Project.

#### 1. Cloud Console Setup
1.  Go to [Google Cloud Console](https://console.cloud.google.com/) and create a new project (e.g., "Mail-Agent").
2.  **Enable APIs:**
    *   Go to **APIs & Services** > **Library**.
    *   Search for and enable **Gmail API** and **Google Calendar API**.
3.  **Configure Consent Screen:**
    *   Go to **APIs & Services** > **OAuth consent screen**.
    *   **User Type:** Select **External** (unless you have a Google Workspace organization).
    *   Fill in app name and email (other fields can be empty).
    *   **Scopes:** Add `.../auth/gmail.modify` and `.../auth/calendar`.
    *   **Test Users:** You don't need to add users if you do the next step immediately.
    *   **IMPORTANT - Production Mode:**
        *   Once created, click **"PUBLISH APP"** button under **Publishing Status**.
        *   Confirm to push to **"In production"**.
        *   *Why?* If you leave it in "Testing", your login tokens will expire every 7 days. In "Production" (even unverified), they last indefinitely.
4.  **Create Credentials:**
    *   Go to **APIs & Services** > **Credentials**.
    *   Click **Create Credentials** > **OAuth client ID**.
    *   **Application type:** Select **Desktop app**.
    *   Download the JSON file, rename it to `credentials.json`, and place it in the root of this project.

#### 2. Local Authentication
Once `credentials.json` is in place, you need to generate the access tokens.

1.  **Run the setup script:**
    ```bash
    python setup_accounts.py
    ```
2.  **Follow the browser prompts:**
    *   The script will open a browser window for each account you have configured.
    *   **"Google hasn't verified this app":** Since you set the app to "Production" but didn't submit it for tedious verification, you will see this warning. This is normal for personal projects.
        *   Click **Advanced**.
        *   Click **Go to [App Name] (unsafe)**.
        *   Click **Continue** / **Allow**.
3.  **Success:**
    *   The script will generate `token.json` (and other token files if multi-account is used).
    *   These tokens are now valid indefinitely (unless you change your password).

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
