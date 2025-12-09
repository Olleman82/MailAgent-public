SYFTE

Syftet med den här appen är att avlasta mig från vardagsmeck i mail och kalender, särskilt:

sortera inkommande mail,

lyfta fram sådant som behöver svar,

få bättre koll på barnens aktiviteter (gymnastik, kör osv)

och automatiskt få relevanta saker in i Google Calendar.

Appen ska fungera som en personlig “mail & kalender-co-pilot” för mitt lab-Googlekonto, inte som en produktionslösning.
Smidighet och snabb testbarhet är viktigare än maximal säkerhet i detta första steg.

Jag tänker kunna köra ett enkelt kommando (t.ex. python main.py) som:

läser mina senaste olästa mail,

klassificerar dem,

skapar etiketter i Gmail,

skapar utkast på svar,

och lägger in kalenderhändelser där det passar.

FUNKTIONELLT MÅL

Bygg en Python-app (CLI eller enkel dev-UI) med Google Agent Development Kit (ADK) som:

Läser mail från mitt lab-Gmail-konto (via Gmail API).

Hittar relaterade mail (samma tråd/samma ärende).

Klassificerar mail i kategorier, t.ex.

Svara – jag behöver svara.

Barnens aktiviteter – gäller barnens gymnastik, kör och liknande.

Övrigt / låg prio.

Gör lätt research vid behov med webbsök (t.ex. för fakta i ett svar).

Skapar utkast på svar i Gmail (inte skicka automatiskt).

Skapar kalenderhändelser i Google Calendar när ett mail innehåller datum/tider för aktiviteter (t.ex. körövning, träning, uppvisning).

Allt ska gå att köra lokalt på min dator mot mitt labbkonto.

1. Målbild (vad agenten ska göra)

En Email & Kalender-agent som:

Läser in nya mail från ditt lab-Gmail-konto.

Hittar relaterade mail (samma tråd / liknande ämne).

Gör lite webbresearch inför svar (Google Search-verktyget).

Klassar mail i kategorier, t.ex.

Svara

Barnens aktiviteter (gymnastik, kör)

Övrigt / låg prio

Skapar utkast på svar, men skickar inte automatiskt.

Skapar kalenderhändelser i Google Calendar när mail innehåller datum/tid för aktiviteter (t.ex. körövning).

Allt körs lokalt från din dator med ett enkelt CLI eller ADK:s dev-UI.

2. Tech-stack (för kod-AI:n)

Be koden bygga med:

Språk: Python 3.10+

Agent-ramverk: Google Agent Development Kit (ADK), python-varianten (google-adk).

LLM-modell: gemini-2.0-flash eller gemini-2.5-flash via Gemini/Vertex (billig & snabb, gratisnivå finns).

Google API:

Gmail API (läsa mail, skapa utkast, sätta labels)

Google Calendar API (skapa events)

Auth: enkel OAuth “Desktop app” med credentials.json + token.json (Gmail/Calendar quickstart-stil).

3. Övergripande arkitektur
3.1 En root-agent i ADK

Bygg en LLM-agent:

Namn: email_hub_agent

Modell: gemini-2.0-flash

Instruktion (fritt formulerat, men ungefär):

Du är en personlig mail- och kalenderassistent.
Du får tillgång till verktyg för Gmail (läsa, hitta relaterade mail, skapa utkast, sätta labels)
och Google Calendar (skapa händelser).
För varje mail ska du:

läsa mail och ev. tidigare tråd,

klassificera den i en av kategorierna,

göra research vid behov,

skapa labels i Gmail,

skapa ett utkast på svar (om det behövs),

skapa kalenderhändelser om mailet beskriver ett möte / aktivitet med datum/tid kring barnens aktiviteter.

Agenten ska ha följande verktyg kopplade:

gmail_list_unread(limit: int)

gmail_get_thread(message_id: str)

gmail_apply_label(message_id: str, label_name: str)

gmail_create_draft_reply(message_id: str, reply_body: str)

gmail_find_related(message_id: str) (t.ex. via subject/same thread)

calendar_create_event(summary: str, start_iso: str, end_iso: str, description: str)

google_search (ADK:s inbyggda verktyg för webbsök).

Alla utom google_search implementeras som custom function tools i ADK (Python).

3.2 Enkelt filupplägg

Be kod-AI:n skapa t.ex.:

project-root/
  main.py               # starta agenten/CLI
  config.py             # läsa env-variabler, paths
  auth/
    google_auth.py      # ansvarar för OAuth + retur av Gmail/Calendar-klienter
  tools/
    gmail_tools.py      # ADK-funktioner som wrappar Gmail API
    calendar_tools.py   # ADK-funktioner som wrappar Calendar API
  agents/
    email_hub_agent.py  # definierar ADK-agenten + instruktioner

4. Funktioner – krav för varje del
4.1 Gmail-verktyg

a) Auth-helper (google_auth.py)

Använd Gmail/Calendar quickstart-mönstret:

Läs credentials.json (OAuth client “Desktop app” du skapar i Google Cloud Console).

Första körning: öppna browser, låt användaren logga in + godkänna.

Spara token.json lokalt.

Ge funktioner:

def get_gmail_service() -> gmail_v1.GmailService: ...
def get_calendar_service() -> calendar_v3.CalendarService: ...


b) gmail_list_unread(limit: int)

Använder users.messages.list med query is:unread och maxResults=limit.

Returnera till agenten en lista av förenklade objekt:

[
  {
    "message_id": "...",
    "thread_id": "...",
    "from": "...",
    "subject": "...",
    "snippet": "...",
    "internal_date": "...(iso)..."
  }
]


c) gmail_get_thread(message_id: str)

Hämta full tråd via users.messages.get (format full).

Plocka ut:

komplett body (text/plain + text/html, basic sanering),

headers: From, To, Subject, Date.

Returnera som strukturerat JSON för agenten.

d) gmail_find_related(message_id: str)

Enkel variant (räcker för test):

Hämta mailet.

Kör en Gmail-search på subject:"<ämne utan Re/Fwd>" eller threadId.

Returnera lista med förenklade meddelanden.

e) gmail_apply_label(message_id: str, label_name: str)

Skapa (vid behov) Gmail-labels:

"AI/Svara"

"AI/Barnens aktiviteter"

"AI/Övrigt"

Cacha name -> labelId i minne (eller fil).

Använd users.messages.modify och sätt addLabelIds=[labelId].

f) gmail_create_draft_reply(message_id: str, reply_body: str)

Hämta mailet, bygg ett korrekt reply-MIME (rätt In-Reply-To, References, Subject: Re: etc).

Använd users.drafts.create i Gmail API.

Returnera draft_id och ev. en länk som du loggar ut.

4.2 Calendar-verktyg

calendar_create_event(...)

Input (från agenten): summary, start_iso, end_iso, description.

Använd Calendar API events.insert mot primary kalender.

Lägg description = kort utdrag av mailet + länk till Gmail (message URL).

Returnera event_id + htmlLink.

4.3 Klassificering & beslut (inne i agenten)

Ge agenten en intern policy (en del av instruktionen):

När du behandlar ett mail ska du alltid:

Bestämma en kategori:

Svara: kräver svar från mig.

Barnens aktiviteter: gäller barnens gymnastik, kör, träningar, uppvisningar osv.

Övrigt: allt annat.

Bestäm:

needs_reply (true/false)

needs_calendar_event (true/false)

Om needs_reply == true:

Gör ev. google_search om du behöver fakta.

Skapa ett kort, vänligt svar på svenska.

Om needs_calendar_event == true:

Försök extrahera datum, tid, plats och titel (ex: "Annie – gymnastikträning").

Om informationen är otydlig: föreslå ett rimligt intervall (ex: 18:00–19:00) och lägg det i description som “osäker tid, dubbelkolla i mailet”.

Resultatet för ett mail ska agenten hålla i ett internt JSON-objekt ungefär så här:

{
  "category": "Barnens aktiviteter",
  "needs_reply": true,
  "needs_calendar_event": true,
  "reply_body": "Hej ...",
  "event": {
    "summary": "Annie – körövning",
    "start_iso": "2025-01-15T18:00:00+01:00",
    "end_iso": "2025-01-15T19:00:00+01:00",
    "description": "Utdrag ur mailet... (och ev osäkerheter)"
  }
}


Sen använder agenten verktygen i rätt ordning:

gmail_apply_label(...)

gmail_create_draft_reply(...) (om needs_reply)

calendar_create_event(...) (om needs_calendar_event)

5. Typiska körflöden
5.1 “Batch triage” (kommando i main.py)

Pseudologik för kod-AI:n:

# main.py
# 1. skapa email_hub_agent + Runner (ADK)
# 2. be agenten göra ett "system call" typ:

"Triagera mina senaste 10 olästa mail. 
  För varje mail: 
    - Klassificera enligt policyn,
    - sätt Gmail-label,
    - skapa ev. utkast på svar,
    - skapa ev. kalenderhändelse.
  Sammanfatta vad du har gjort i slutsvaret."


Agenten använder sen sina Gmail/Calendar-verktyg själv.

5.2 Interaktivt läge (valfritt)

Du kan också låta kod-AI:n koppla in ADK:s dev-UI (web UI som följer med quickstart), så du kan chatta med agenten:
“Visa alla mail om barnens körövningar den här veckan” osv.

6. Enkel inloggning (uppfyller “smidighet > säkerhet”)

I specen till kod-AI:n, skriv ungefär:

Följ Googles “Gmail API Python quickstart”-mönster för OAuth 2.0: credentials.json + token.json i projektroten.

Använd samma token.json för både Gmail och Calendar (lägg till båda scopena när användaren loggar in första gången).



OBS! gemini-flash-latest är den AI modell hos google som vi ska använda. Kräövs snabba svar kan du överväga att använda geminiflash-latest-lite för delar av flödet.

NEdan ett typiskt python kod:

# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-flash-latest"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinkingConfig: {
            thinkingBudget: 0,
        },
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()


NOTERA! Om du vill aktivera thinkng mode å ändrar du värdet på thinkingydget till= -1