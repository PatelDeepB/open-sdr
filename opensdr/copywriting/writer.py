from typing import Dict, Optional

from opensdr.copywriting.deliverability import audit_email_deliverability
from opensdr.copywriting.templates import render_template
from opensdr.models import CampaignStatus, Lead


class CopywriterAgent:
    """Generates personalized multi-step email copy and audits spam safety."""

    def __init__(self, sender_name: str = "Alex", sender_company: str = "OpenSDR"):
        self.sender_name = sender_name
        self.sender_company = sender_company

    def build_icebreaker(self, lead: Lead) -> str:
        """Create a bespoke opening line utilizing firmographic research signals."""
        if lead.company_info and lead.company_info.tech_stack:
            primary_tech = lead.company_info.tech_stack[0]
            return f"Noticed {lead.company_name} is actively leveraging {primary_tech} to power your stack."

        if lead.company_info and lead.company_info.signals:
            return f"Loved seeing your team's momentum and growth over at {lead.domain}."

        return f"Impressive work you and the team are driving at {lead.company_name}."

    def generate_sequence(self, lead: Lead, template_name: str = "quick_question") -> Dict[str, Dict[str, str]]:
        """Produce initial email, follow-up bump, and breakup email for the lead."""
        pain_point = "scaling outbound qualified meetings without expensive headcount"
        if lead.company_info and lead.company_info.summary:
            pain_point = f"optimizing sales operations across {lead.domain}"

        icebreaker = self.build_icebreaker(lead)
        variables = {
            "first_name": lead.first_name,
            "company_name": lead.company_name,
            "pain_point": pain_point,
            "icebreaker": icebreaker,
            "sender_name": self.sender_name
        }

        step_1 = render_template(template_name, variables)
        variables["original_subject"] = step_1["subject"]
        step_2 = render_template("followup_bump", variables)
        step_3 = render_template("breakup", variables)

        return {
            "step_1": step_1,
            "step_2": step_2,
            "step_3": step_3
        }

    def process_lead(self, lead: Lead, template_name: str = "quick_question") -> Lead:
        """Generate email sequences, run deliverability audit, and update lead state."""
        sequence = self.generate_sequence(lead, template_name)
        step_1_audit = audit_email_deliverability(
            subject=sequence["step_1"]["subject"],
            body=sequence["step_1"]["body"]
        )

        lead.generated_copy = {
            "initial_subject": sequence["step_1"]["subject"],
            "initial_body": sequence["step_1"]["body"],
            "followup_subject": sequence["step_2"]["subject"],
            "followup_body": sequence["step_2"]["body"],
            "breakup_subject": sequence["step_3"]["subject"],
            "breakup_body": sequence["step_3"]["body"],
            "deliverability_score": str(step_1_audit.score)
        }
        lead.campaign_status = CampaignStatus.COPY_GENERATED
        lead.metadata["deliverability_safe"] = step_1_audit.is_safe
        return lead
