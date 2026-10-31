import asyncio
from typing import List, Optional

from opensdr.copywriting.writer import CopywriterAgent
from opensdr.db import get_default_engine, save_or_update_lead
from opensdr.enrichment.waterfall import WaterfallEnricher
from opensdr.jobs.queue import JobQueueManager
from opensdr.models import Lead
from opensdr.research.agent import ResearchAgent
from sqlalchemy.orm import sessionmaker


async def process_single_lead(
    lead: Lead,
    enricher: WaterfallEnricher,
    researcher: ResearchAgent,
    copywriter: CopywriterAgent
) -> Lead:
    """Execute enrich -> research -> copywrite chain on a single lead."""
    lead = await enricher.run(lead)
    lead = await researcher.analyze(lead)
    lead = copywriter.process_lead(lead)
    return lead


async def run_batch_enrichment_worker(
    job_id: str,
    leads: List[Lead],
    job_manager: JobQueueManager,
    db_session_factory: Optional[sessionmaker] = None
) -> None:
    """Asynchronous background task processing a list of leads."""
    job_manager.mark_running(job_id)
    enricher = WaterfallEnricher()
    researcher = ResearchAgent()
    copywriter = CopywriterAgent()

    factory = db_session_factory
    if factory is None:
        engine = get_default_engine()
        factory = sessionmaker(bind=engine)

    for lead in leads:
        try:
            processed = await process_single_lead(lead, enricher, researcher, copywriter)
            with factory() as session:
                save_or_update_lead(session, processed)
            job_manager.update_progress(job_id, success=True)
        except Exception as e:
            job_manager.update_progress(job_id, success=False, error=str(e))
