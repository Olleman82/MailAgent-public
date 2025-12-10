# Mail & Calendar Copilot (Google ADK)

A powerful, agentic AI assistant for Gmail and Google Calendar. It uses Google's Agent Development Kit (ADK) and Gemini Pro to intelligently triage emails, draft replies, and manage calendar events.

**Imagine a personal executive assistant who knows your schedule, remembers your past conversations, and even suggests great entertainment—but it's an AI running securely on your machine.**

This isn't just a script; it's a **Multi-Agent System**. A smart "Orchestrator" reads your email and instantly delegates tasks to specialized experts:
*   🧠 **The Historian (Context Agent):** Digs through years of email history to find that one specific detail you forgot ("What hotel did we stay at in 2018?").
*   📅 **The Secretary (Calendar Agent):** Manages your schedule, negotiates times, handles conflicts, and books family events seamlessly.
*   📻 **The Entertainer (Radio Agent):** Knows exactly what's good on the radio right now, finding podcasts and programs that match your mood or upcoming trip.
*   🌐 **The Researcher (Grounded Search):** Fact-checks vague requests via Google Search so you get precise answers.

**Real-world Use Cases:**
1.  **"The Time Saver":** Receive an email about a soccer match? The agent checks your family calendar for conflicts, books it, and marks the email as processed—all before you even open your inbox.
2.  **"The Memory Jog":** An old friend asks for a recipe you sent years ago. The agent searches your history, finds the exact email from 2015, extracts the recipe, and drafts a reply for you.
3.  **"The Trip Planner":** Going on a road trip? The agent reads your travel dates and proactively suggests 3 perfect podcasts from Sveriges Radio to listen to in the car.

---

**Technical Overview:**
*   **Multi-agent Orchestration:** A main email hub agent delegates tasks to specialized sub-agents.
*   **Intelligent Triage:** Categorizes emails (Reply Needed, Calendar/Activities, Other) and labels them automatically.
*   **Smart Replies:** Drafts replies based on email thread context and extracted attachments.
*   **Calendar Management:** Checks for conflicts before booking and handles event scheduling.
*   **Attachment Handling:** Reads and extracts text from PDF, Word, and Excel attachments locally to provide full context to agents.
*   **External Real-time Info:** Uses Grounded Google Search for up-to-date info and Sveriges Radio (SR) MCP for Swedish radio recommendations.

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
    *   Create a `.env` file in the root directory:
        ```bash
        GEMINI_API_KEY=your_api_key_here
        GEMINI_MODEL=gemini-flash-latest
        ```

### 🔑 Google Cloud & Authentication Setup

To allow the agent to access your email and calendar, you need a Google Cloud Project with the correct credentials.

#### 1. Cloud Console Setup
1.  Go to [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2.  **Enable APIs:**
    *   Go to **APIs & Services** > **Library**.
    *   Search for and enable **Gmail API** and **Google Calendar API**.
3.  **Configure Consent Screen:**
    *   Go to **APIs & Services** > **OAuth consent screen**.
    *   **User Type:** Select **External**.
    *   **Scopes:** Add `.../auth/gmail.modify` and `.../auth/calendar`.
    *   **Publish App:** Push the app to "In production" (even if unverified) to avoid 7-day token expiration.
4.  **Create Credentials:**
    *   Go to **APIs & Services** > **Credentials**.
    *   Click **Create Credentials** > **OAuth client ID**.
    *   **Application type:** Desktop app.
    *   Download the JSON file, rename it to `credentials.json`, and place it in the project root.

#### 2. Local Authentication
1.  **Run the setup script:**
    ```bash
    python setup_accounts.py
    ```
2.  **Follow the browser prompts** to log in with your primary Google account.
3.  This will generate `token.json`.

## 🤖 Agent Architecture

- **Orchestrator (Hub Agent):** The main manager that reads emails, classifies them, and delegates tasks.
- **Context/Research Agent:** Searches your email history for long-term memory and context.
- **Calendar Agent:** Manages your schedule, checks conflicts, and books events.
- **Radio Agent:** Specialized in Swedish Radio (SR) content (can be replaced/disabled if not needed).
- **Grounded Search Agent:** Performs Google Searches for external queries.

### Customization

The agent behavior is defined by instruction files.
- **Default behavior:** Defined in `*.default.txt` files (generic, single mailbox).
- **Custom behavior:** Create your own `*.txt` files (e.g., `agent_instruction.txt`) to override the defaults. These files are ignored by git, preventing accidental leaks of personal instructions.

## 🏃 Usage

**Run a one-time triage of your last 10 emails:**
```bash
python main.py --limit 10
```

**Run in Watchdog Mode (Continuous):**
Checks for new emails periodically.
```bash
python main.py --watch --interval 60
```
