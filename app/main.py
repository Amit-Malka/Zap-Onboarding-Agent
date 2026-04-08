from pydantic import BaseModel
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

app = FastAPI(title="zap-onboarding-agent")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class RunOnboardingRequest(BaseModel):
    dapayzahav_url: str


async def scrape_digital_assets(dapayzahav_url: str) -> dict:
    from app.scraper import scrape_digital_assets as scraper_step

    return await scraper_step(dapayzahav_url)


def extract_business_data(raw_text: str, source_url: str) -> dict:
    from app.extractor import extract_business_data as extractor_step

    return extractor_step(raw_text, source_url)


def build_customer_card(extracted_data: dict) -> dict:
    from app.card_generator import build_customer_card as card_step

    return card_step(extracted_data)


def generate_onboarding_script(customer_card: dict) -> str:
    from app.script_generator import generate_onboarding_script as script_step

    return script_step(customer_card)


def log_to_crm(customer_card: dict, onboarding_script: str) -> bool:
    from app.crm_logger import log_to_crm as crm_step

    return crm_step(customer_card, onboarding_script)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.post("/run-onboarding")
async def run_onboarding(payload: RunOnboardingRequest) -> dict:
    try:
        scraped_data = await scrape_digital_assets(payload.dapayzahav_url)
    except Exception as error:
        raise HTTPException(
            status_code=500, detail=f"Onboarding failed at scraper: {error}"
        ) from error

    try:
        extracted_data = extract_business_data(
            scraped_data.get("dapayzahav_raw", ""),
            scraped_data.get("source_url", payload.dapayzahav_url),
        )
    except Exception as error:
        raise HTTPException(
            status_code=500, detail=f"Onboarding failed at extractor: {error}"
        ) from error

    try:
        customer_card = build_customer_card(extracted_data)
    except Exception as error:
        raise HTTPException(
            status_code=500, detail=f"Onboarding failed at card_generator: {error}"
        ) from error

    try:
        onboarding_script = generate_onboarding_script(customer_card)
    except Exception as error:
        raise HTTPException(
            status_code=500, detail=f"Onboarding failed at script_generator: {error}"
        ) from error

    try:
        crm_logged = log_to_crm(customer_card, onboarding_script)
    except Exception as error:
        raise HTTPException(
            status_code=500, detail=f"Onboarding failed at crm_logger: {error}"
        ) from error

    return {
        "customer_card": customer_card,
        "onboarding_script": onboarding_script,
        "crm_logged": crm_logged,
        "missing_fields": customer_card.get("missing_fields", []),
    }
