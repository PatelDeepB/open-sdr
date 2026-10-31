from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from opensdr.campaigns.dispatcher import (
    BaseDispatcher,
    InboxAccount,
    InboxRotator,
    MockDispatcher,
)
from opensdr.models import CampaignStatus, Lead


class CampaignStats(BaseModel):
    """Real-time analytics and performance metrics for a campaign."""
    total_leads: int = 0
    sent_count: int = 0
    replied_count: int = 0
    bounced_count: int = 0
    reply_rate: float = 0.0
    bounce_rate: float = 0.0


class Campaign(BaseModel):
    """Campaign definition containing targeted prospects and metadata."""
    id: str
    name: str
    leads: List[Lead] = Field(default_factory=list)
    stats: CampaignStats = Field(default_factory=CampaignStats)


class CampaignOrchestrator:
    """Manages the full lifecycle of an outbound email campaign."""

    def __init__(self, rotator: InboxRotator, dispatcher: Optional[BaseDispatcher] = None):
        self.rotator = rotator
        self.dispatcher = dispatcher or MockDispatcher()

    async def dispatch_next_step(self, campaign: Campaign) -> CampaignStats:
        """Process queued leads and dispatch their initial outreach emails."""
        for lead in campaign.leads:
            if not lead.email or lead.campaign_status != CampaignStatus.COPY_GENERATED:
                continue

            inbox = self.rotator.get_next_available_inbox()
            if not inbox:
                break  # All inboxes reached their daily capacity

            subject = lead.generated_copy.get("initial_subject", "")
            body = lead.generated_copy.get("initial_body", "")

            dispatched = await self.dispatcher.send_message(
                sender_inbox=inbox,
                recipient_email=lead.email,
                subject=subject,
                body=body
            )

            if dispatched:
                lead.campaign_status = CampaignStatus.SENT
                campaign.stats.sent_count += 1

        self._refresh_stats(campaign)
        return campaign.stats

    def record_lead_reply(self, campaign: Campaign, recipient_email: str) -> bool:
        """Mark a lead as replied and update campaign metrics."""
        for lead in campaign.leads:
            if lead.email and lead.email.lower() == recipient_email.lower():
                lead.campaign_status = CampaignStatus.REPLIED
                campaign.stats.replied_count += 1
                self._refresh_stats(campaign)
                return True
        return False

    def record_lead_bounce(self, campaign: Campaign, recipient_email: str) -> bool:
        """Mark a lead as bounced and recalculate deliverability metrics."""
        for lead in campaign.leads:
            if lead.email and lead.email.lower() == recipient_email.lower():
                lead.campaign_status = CampaignStatus.BOUNCED
                campaign.stats.bounced_count += 1
                self._refresh_stats(campaign)
                return True
        return False

    def _refresh_stats(self, campaign: Campaign) -> None:
        total = len(campaign.leads)
        sent = campaign.stats.sent_count
        campaign.stats.total_leads = total
        if sent > 0:
            campaign.stats.reply_rate = round(campaign.stats.replied_count / sent, 4)
            campaign.stats.bounce_rate = round(campaign.stats.bounced_count / sent, 4)
