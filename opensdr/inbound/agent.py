from typing import Optional
from pydantic import BaseModel

from opensdr.inbound.classifier import ReplyIntent, classify_inbound_reply
from opensdr.models import CampaignStatus, Lead


class InboundActionResponse(BaseModel):
    """Result of an autonomous SDR evaluation on an inbound prospect reply."""
    intent: ReplyIntent
    confidence: float
    draft_subject: str
    draft_body: str
    updated_lead_status: CampaignStatus
    referral_lead: Optional[Lead] = None
    is_suppressed: bool = False


class InboundSDRAgent:
    """Autonomous SDR agent that parses replies and generates next actions."""

    def __init__(self, booking_url: str = "https://cal.com/team/15min", sender_name: str = "Alex"):
        self.booking_url = booking_url
        self.sender_name = sender_name

    def process_reply(self, lead: Lead, reply_text: str) -> InboundActionResponse:
        """Evaluate reply text and determine next automated sales step."""
        analysis = classify_inbound_reply(reply_text)

        if analysis.intent == ReplyIntent.UNSUBSCRIBE:
            lead.metadata["suppressed"] = True
            lead.metadata["unsubscribed"] = True
            return InboundActionResponse(
                intent=analysis.intent,
                confidence=analysis.confidence,
                draft_subject=f"Unsubscribed: {lead.company_name}",
                draft_body="Understood. You have been removed from our list. Have a great day.",
                updated_lead_status=CampaignStatus.BOUNCED,
                is_suppressed=True
            )

        if analysis.intent == ReplyIntent.INTERESTED:
            lead.campaign_status = CampaignStatus.REPLIED
            body = (
                f"Hi {lead.first_name},\n\n"
                f"Great to hear! Here is my direct calendar link to pick a convenient 15-minute slot:\n"
                f"{self.booking_url}\n\n"
                f"Looking forward to speaking soon.\n\n"
                f"Best,\n{self.sender_name}"
            )
            return InboundActionResponse(
                intent=analysis.intent,
                confidence=analysis.confidence,
                draft_subject=f"re: meeting link for {lead.company_name}",
                draft_body=body,
                updated_lead_status=CampaignStatus.REPLIED
            )

        if analysis.intent == ReplyIntent.WRONG_PERSON and analysis.referral_email:
            referral_lead = Lead(
                first_name="Colleague",
                last_name="Referral",
                company_name=lead.company_name,
                domain=lead.domain,
                email=analysis.referral_email,
                metadata={"referred_by": lead.email}
            )
            body = (
                f"Hi {lead.first_name},\n\n"
                f"Appreciate the redirect! I will reach out to {analysis.referral_email} directly.\n\n"
                f"Thanks again,\n{self.sender_name}"
            )
            return InboundActionResponse(
                intent=analysis.intent,
                confidence=analysis.confidence,
                draft_subject=f"re: thanks for the introduction at {lead.company_name}",
                draft_body=body,
                updated_lead_status=CampaignStatus.REPLIED,
                referral_lead=referral_lead
            )

        # Default Neutral response
        body = (
            f"Hi {lead.first_name},\n\n"
            f"Thanks for getting back to me. Would you be open to a quick 5-minute call later this week?\n\n"
            f"Best,\n{self.sender_name}"
        )
        return InboundActionResponse(
            intent=analysis.intent,
            confidence=analysis.confidence,
            draft_subject=f"re: follow up re: {lead.company_name}",
            draft_body=body,
            updated_lead_status=CampaignStatus.REPLIED
        )
