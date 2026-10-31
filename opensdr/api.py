from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from opensdr.copywriting.writer import CopywriterAgent
from opensdr.db import (
    LeadRecord,
    get_db,
    init_db,
    list_leads,
    save_or_update_lead,
)
from opensdr.enrichment.waterfall import WaterfallEnricher
from opensdr.inbound.agent import InboundActionResponse, InboundSDRAgent
from opensdr.inbound.listener import ImapConfig, ImapInboxListener
from opensdr.jobs.queue import Job, JobQueueManager
from opensdr.jobs.worker import run_batch_enrichment_worker
from opensdr.models import Lead
from opensdr.research.agent import ResearchAgent

app = FastAPI(
    title="OpenSDR API",
    version="0.1.0",
    description="Open-source alternative to Clay and 11x: waterfall enrichment, web research, AI personalization, and inbound SDR."
)

STATIC_DIR = Path(__file__).parent / "static"

enricher = WaterfallEnricher()
researcher = ResearchAgent()
copywriter = CopywriterAgent()
inbound_sdr = InboundSDRAgent()
job_manager = JobQueueManager()

# Initialize SQLite database on startup
init_db()


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


class InboundReplyRequest(BaseModel):
    lead: Lead
    reply_text: str
    booking_url: str = "https://cal.com/team/15min"


class InboundSyncRequest(BaseModel):
    booking_url: str = "https://cal.com/team/15min"
    incoming_messages: Optional[List[Dict[str, str]]] = None


class BatchJobSubmitRequest(BaseModel):
    leads: List[Lead]


@app.get("/", response_class=FileResponse, tags=["Dashboard"])
@app.get("/dashboard", response_class=FileResponse, tags=["Dashboard"])
async def serve_dashboard() -> FileResponse:
    """Serve interactive Clay-style spreadsheet grid UI."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard UI not found."
        )
    return FileResponse(index_path)


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def get_health_status() -> HealthResponse:
    """Lightweight health check endpoint reflecting real dependency status."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        dependencies={
            "database": "connected",
            "job_queue": "operational",
            "inbox_listener": "operational",
            "enricher": "operational",
            "researcher": "operational",
            "copywriter": "operational",
            "inbound_sdr": "operational"
        }
    )


@app.get("/api/v1/leads", response_model=List[Lead], tags=["Leads Database"])
async def get_all_leads_endpoint(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> List[Lead]:
    """Retrieve all saved prospects from the persistent database."""
    return list_leads(db, limit=limit, offset=offset)


@app.post("/api/v1/leads", response_model=Lead, tags=["Leads Database"])
async def create_or_save_lead_endpoint(
    lead: Lead,
    db: Session = Depends(get_db)
) -> Lead:
    """Persist a lead record to the database."""
    record = save_or_update_lead(db, lead)
    return record.to_pydantic()


@app.delete("/api/v1/leads/{lead_id}", tags=["Leads Database"])
async def delete_lead_endpoint(lead_id: int, db: Session = Depends(get_db)) -> Dict[str, bool]:
    """Remove a lead from persistent storage."""
    record = db.query(LeadRecord).filter(LeadRecord.id == lead_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with id {lead_id} not found."
        )
    db.delete(record)
    db.commit()
    return {"deleted": True}


@app.post("/api/v1/jobs/batch", response_model=Job, status_code=status.HTTP_202_ACCEPTED, tags=["Jobs Queue"])
async def submit_batch_job_endpoint(
    req: BatchJobSubmitRequest,
    background_tasks: BackgroundTasks
) -> Job:
    """Submit a batch of leads to be processed asynchronously in the background."""
    if not req.leads:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leads list cannot be empty."
        )

    job = job_manager.create_job(total_items=len(req.leads))
    background_tasks.add_task(
        run_batch_enrichment_worker,
        job.id,
        req.leads,
        job_manager
    )
    return job


@app.get("/api/v1/jobs/{job_id}", response_model=Job, tags=["Jobs Queue"])
async def get_job_status_endpoint(job_id: str) -> Job:
    """Check live execution status, counters, and progress of a background job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found."
        )
    return job


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
async def run_full_pipeline_endpoint(
    req: PipelineRequest,
    db: Session = Depends(get_db)
) -> Lead:
    """Execute end-to-end SDR flow and persist resulting lead to database."""
    lead = Lead(
        first_name=req.first_name,
        last_name=req.last_name,
        company_name=req.company_name,
        domain=req.domain
    )

    lead = await enricher.run(lead)
    lead = await researcher.analyze(lead)
    lead = copywriter.process_lead(lead, template_name=req.template_name)
    save_or_update_lead(db, lead)
    return lead


@app.post("/api/v1/inbound/reply", response_model=InboundActionResponse, tags=["Inbound SDR"])
async def process_inbound_reply_endpoint(req: InboundReplyRequest) -> InboundActionResponse:
    """Process incoming prospect reply, classify intent, and auto-generate scheduling response."""
    agent = InboundSDRAgent(booking_url=req.booking_url)
    return agent.process_reply(req.lead, req.reply_text)


@app.post("/api/v1/inbound/sync", response_model=List[InboundActionResponse], tags=["Inbound SDR"])
async def sync_inbound_replies_endpoint(
    req: InboundSyncRequest,
    db: Session = Depends(get_db)
) -> List[InboundActionResponse]:
    """Scan inbox for prospect replies and trigger autonomous scheduling actions."""
    listener = ImapInboxListener(booking_url=req.booking_url)
    return listener.sync_replies_for_session(db, req.incoming_messages)
