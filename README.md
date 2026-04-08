# Zap Onboarding Agent

Zap Onboarding Agent automates the early customer onboarding workflow for small businesses listed on Dapay Zahav. Instead of manually collecting profile details, preparing a call brief, writing a personalized onboarding script, and logging everything into CRM, this project executes the full pipeline in one flow: scrape public listing data, extract structured business context with an LLM, generate a customer card, produce a call-ready script, and log the result to Google Sheets, all behind a single FastAPI web interface.

## Architecture

```text
+------------------+
| URL Input (UI)   |
+--------+---------+
         |
         v
+--------------------------+
| Scraper (crawl4ai)       |
| - profile page markdown  |
+------------+-------------+
             |
             v
+-------------------------------+
| Extractor (LangChain + Groq)  |
| - structured business fields  |
+---------------+---------------+
                |
                v
+-------------------------------+
| Card Generator                |
| - customer card + gaps        |
+---------------+---------------+
                |
                v
+-------------------------------+
| Script Generator              |
| - onboarding call script      |
+---------------+---------------+
                |
                v
+-------------------------------+
| CRM Logger (Google Sheets)    |
| - append onboarding record    |
+---------------+---------------+
                |
                v
+-------------------------------+
| UI + API Response (FastAPI)   |
| - card, script, CRM status    |
+-------------------------------+
```

## Tech Stack

| Tool | Purpose | Why Chosen |
|---|---|---|
| FastAPI | Web server, API endpoints, template serving | Lightweight, async-friendly, clear request/response modeling |
| Jinja2 | Single-page UI templating | Simple server-rendered UI with minimal overhead |
| crawl4ai | Public profile scraping | Better suited for dynamic web extraction than static HTML parsers |
| LangChain | Prompt orchestration and LLM flow | Clean abstraction for extraction and generation chains |
| Groq (`qwen/qwen3-32b`) | Fast inference for extraction and script generation | Low latency and accessible free tier for rapid iteration |
| Google Sheets (gspread) | Mock CRM storage | Zero infrastructure setup and easy non-technical visibility |
| pytest | Test validation | Fast feedback loop and reliable regression checks |

## Setup

### 1) Clone repository

```bash
git clone <your-repo-url>
cd zap-onboarding-agent
```

### 2) Create and populate environment variables

Create `.env` in project root:

```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account", "...":"..."}
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
```

Notes:
- `GOOGLE_SERVICE_ACCOUNT_JSON` must be a valid JSON string (single-line is easiest).
- `GOOGLE_SHEETS_SPREADSHEET_ID` is the ID segment from the Google Sheets URL.

### 3) Google Sheets service account setup

1. Create a Google Cloud project.
2. Enable Google Sheets API (and Google Drive API).
3. Create a Service Account and generate a JSON key.
4. Copy JSON key content into `GOOGLE_SERVICE_ACCOUNT_JSON`.
5. Create a Google Sheet for CRM logging.
6. Share the sheet with the service account email (Editor access).
7. Copy sheet ID into `GOOGLE_SHEETS_SPREADSHEET_ID`.

### 4) Install dependencies

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 5) Run the app

```bash
uvicorn app.main:app --reload
```

Open: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Usage

1. Open the web UI.
2. Paste a Dapay Zahav business URL.
3. Click **Run Onboarding**.
4. Review:
   - Customer Card
   - Onboarding Script
   - CRM logging toast status

### Screenshot

`[Screenshot placeholder: docs/images/onboarding-ui.png]`

### Example API Output

```json
{
  "customer_card": {
    "card_id": "b6b2d3ee-3f80-49ea-a508-39e6ac314d8e",
    "created_at": "2026-04-08T14:35:12.421921+00:00",
    "business_name": "Acme Plumbing",
    "owner_name": null,
    "phone": "03-5551234",
    "whatsapp": null,
    "address": "12 Herzl St, Tel Aviv",
    "area": "Tel Aviv",
    "category": "Plumbing",
    "services": ["Emergency plumbing", "Pipe repair"],
    "service_areas": ["Tel Aviv", "Ramat Gan"],
    "working_hours": "Sun-Thu 08:00-18:00",
    "rating": "4.7",
    "review_count": 83,
    "about_text": "Trusted local plumbing services.",
    "source_url": "https://www.d.co.il/...",
    "has_personal_website": false,
    "missing_fields": ["owner_name", "whatsapp"]
  },
  "onboarding_script": "## Opening\n...\n## Confirm Existing Details\n...\n## Value Proposition\n...\n## Discovery Questions\n...\n## Next Step\n...",
  "crm_logged": true,
  "missing_fields": ["owner_name", "whatsapp"]
}
```

## Design Decisions

- **crawl4ai over BeautifulSoup**: Dapay Zahav pages can include dynamic or JS-influenced content. `crawl4ai` provides richer crawling behavior and markdown extraction, while BeautifulSoup alone is best for static HTML parsing.
- **Groq over OpenAI**: Groq provides very fast response times and a developer-friendly free tier, which is practical for iterative extraction and script generation in early-stage products.
- **Google Sheets as mock CRM**: It requires almost no infrastructure, is easy to audit manually, and is immediately understandable across technical and non-technical stakeholders.
- **Edge case: no personal website**: The extractor explicitly includes `has_personal_website` and supports null/empty values for missing business data; card generation surfaces missing fields so reps can complete them during the call.

## Limitations & Future Improvements

- Add robust retry/backoff and structured observability around scraping/LLM/CRM steps.
- Support multilingual script generation with selectable call tone templates.
- Replace Sheets with a production CRM connector (HubSpot/Salesforce/Zoho) and add idempotency controls.
