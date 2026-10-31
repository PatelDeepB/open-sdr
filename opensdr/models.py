import enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EmailStatus(str, enum.Enum):
    """Deliverability verification status for email addresses."""
    VERIFIED = "verified"
    ACCEPT_ALL = "accept_all"
    RISKY = "risky"
    INVALID = "invalid"
    UNKNOWN = "unknown"


class CampaignStatus(str, enum.Enum):
    """Pipeline progression stage for a lead."""
    NEW = "new"
    ENRICHED = "enriched"
    RESEARCHED = "researched"
    COPY_GENERATED = "copy_generated"
    QUEUED = "queued"
    SENT = "sent"
    REPLIED = "replied"
    BOUNCED = "bounced"


class Company(BaseModel):
    """Firmographic details for a targeted company."""
    name: str
    domain: str
    industry: Optional[str] = None
    size: Optional[str] = None
    summary: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)
    signals: List[str] = Field(default_factory=list)


class Lead(BaseModel):
    """Target prospect profile and interaction history."""
    id: Optional[str] = None
    first_name: str
    last_name: str
    company_name: str
    domain: str
    title: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    email_status: EmailStatus = EmailStatus.UNKNOWN
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    company_info: Optional[Company] = None
    research_summary: Optional[str] = None
    generated_copy: Dict[str, str] = Field(default_factory=dict)
    campaign_status: CampaignStatus = CampaignStatus.NEW
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EmailVerificationResult(BaseModel):
    """Granular verification results for an email candidate."""
    email: str
    status: EmailStatus
    has_mx_record: bool
    is_disposable: bool
    syntax_valid: bool
    confidence: float
    reason: str


class EnrichmentResult(BaseModel):
    """Output from an enrichment provider within the waterfall."""
    provider_name: str
    found: bool
    email: Optional[str] = None
    status: EmailStatus = EmailStatus.UNKNOWN
    confidence: float = 0.0
    extra_details: Dict[str, Any] = Field(default_factory=dict)
