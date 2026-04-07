# zap-onboarding-agent

Starter scaffold for a FastAPI-based onboarding agent with scraping, extraction, card generation, script generation, and CRM logging modules.

## Project structure

- `app/` application modules
- `templates/` Jinja2 templates
- `static/` static assets
- `tests/` unit tests

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Start the app:
   - `uvicorn app.main:app --reload`
