import abc
import os
from typing import Dict, Optional

from opensdr.models import Company, Lead
from opensdr.research.crawler import (
    detect_tech_signals,
    fetch_domain_summary,
)


class BaseSynthesizer(abc.ABC):
    """Abstract interface for summarizing research data."""

    @abc.abstractmethod
    async def synthesize(self, lead: Lead, page_data: Dict[str, str]) -> Dict[str, str]:
        """Produce structured company insights from extracted page data."""
        pass


class HeuristicSynthesizer(BaseSynthesizer):
    """Deterministic, zero-cost synthesizer extracting core insights from metadata."""

    async def synthesize(self, lead: Lead, page_data: Dict[str, str]) -> Dict[str, str]:
        title = page_data.get("title", "")
        description = page_data.get("meta_description", "")
        body = page_data.get("body_snippet", "")

        summary = description or title or f"{lead.company_name} is operating in the {lead.domain} domain."
        
        # Identify probable customer pain points based on industry signals
        pain_points = "Automating pipeline bottlenecks and scaling outbound revenue without adding headcount."
        trigger = f"Active web presence and digital customer acquisition at {lead.domain}."

        if "b2b" in body.lower() or "enterprise" in body.lower():
            pain_points = "Streamlining long enterprise sales cycles and improving account-based targeting."
        elif "ecommerce" in body.lower() or "store" in body.lower():
            pain_points = "Lowering customer acquisition costs and driving repeat cart conversions."

        return {
            "summary": summary,
            "pain_points": pain_points,
            "trigger": trigger
        }


class ResearchAgent:
    """Autonomous agent that crawls company domains and extracts structured intelligence."""

    def __init__(self, synthesizer: Optional[BaseSynthesizer] = None):
        self.synthesizer = synthesizer or HeuristicSynthesizer()

    async def analyze(self, lead: Lead) -> Lead:
        """Execute full company investigation and attach firmographic research to lead."""
        if not lead.domain:
            return lead

        page_data = await fetch_domain_summary(lead.domain)
        tech_stack = detect_tech_signals(page_data.get("raw_html", ""))
        insights = await self.synthesizer.synthesize(lead, page_data)

        lead.company_info = Company(
            name=lead.company_name,
            domain=lead.domain,
            summary=insights.get("summary"),
            tech_stack=tech_stack,
            signals=[insights.get("trigger", "")]
        )
        lead.research_summary = (
            f"Summary: {insights.get('summary')} | "
            f"Pain Point: {insights.get('pain_points')} | "
            f"Signals: {', '.join(tech_stack) if tech_stack else 'Standard Stack'}"
        )
        lead.metadata["research_completed"] = True
        return lead
