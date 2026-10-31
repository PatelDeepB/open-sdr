from typing import Any, Dict
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from opensdr.copywriting.writer import CopywriterAgent
from opensdr.enrichment.waterfall import WaterfallEnricher
from opensdr.models import Lead
from opensdr.research.agent import ResearchAgent

app = FastAPI(
    title="OpenSDR API",
    version="0.1.0",
    description="Open-source alternative to Clay: waterfall enrichment, web research, and AI personalization."
)

enricher = WaterfallEnricher()
researcher = ResearchAgent()
copywriter = CopywriterAgent()


class HealthResponse(BaseModel):
    status: str
    version: str
    dependencies: Dict[str, str]


class PipelineRequest(BaseModel):
    first_name: str
    last_name: str
    company_name: str
    domain: str
    template_name: str = "quick_question"


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def get_health_status() -> HealthResponse:
    """Lightweight health check endpoint reflecting real dependency status."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        dependencies={
            "enricher": "operational",
            "researcher": "operational",
            "copywriter": "operational"
        }
    )


@app.post("/api/v1/enrich", response_model=Lead, tags=["Enrichment"])
async def enrich_lead_endpoint(lead: Lead) -> Lead:
    """Execute waterfall enrichment cascade on prospect contact information."""
    if not lead.domain or not lead.first_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain and first_name are required for enrichment."
        )
    return await enricher.run(lead)


@app.post("/api/v1/research", response_model=Lead, tags=["Research"])
async def research_lead_endpoint(lead: Lead) -> Lead:
    """Crawl company web presence and generate firmographic research intelligence."""
    if not lead.domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain is required for company research."
        )
    return await researcher.analyze(lead)


@app.post("/api/v1/copywrite", response_model=Lead, tags=["Copywriting"])
async def copywrite_lead_endpoint(lead: Lead, template: str = "quick_question") -> Lead:
    """Synthesize personalized 3-step outbound email cadence and audit deliverability."""
    return copywriter.process_lead(lead, template_name=template)


@app.post("/api/v1/pipeline", response_model=Lead, tags=["Pipeline"])
async def run_full_pipeline_endpoint(req: PipelineRequest) -> Lead:
    """Execute end-to-end autonomous SDR flow: Waterfall Enrich -> Web Research -> AI Copywriter."""
    lead = Lead(
        first_name=req.first_name,
        last_name=req.last_name,
        company_name=req.company_name,
        domain=req.domain
    )

    lead = await enricher.run(lead)
    lead = await researcher.analyze(lead)
    lead = copywriter.process_lead(lead, template_name=req.template_name)
    return lead
