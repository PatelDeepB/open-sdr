import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from opensdr.models import CampaignStatus, Company, EmailStatus, Lead

Base = declarative_base()


class LeadRecord(Base):
    """Database model for persistent lead storage."""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company_name = Column(String(150), nullable=False)
    domain = Column(String(150), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    email_status = Column(String(50), default="unknown")
    confidence_score = Column(Float, default=0.0)
    tech_stack_json = Column(Text, default="[]")
    research_summary = Column(Text, nullable=True)
    generated_copy_json = Column(Text, default="{}")
    campaign_status = Column(String(50), default="new")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_pydantic(self) -> Lead:
        """Convert database record to domain Lead model."""
        tech = json.loads(self.tech_stack_json or "[]")
        copy = json.loads(self.generated_copy_json or "{}")
        meta = json.loads(self.metadata_json or "{}")

        company = Company(
            name=self.company_name,
            domain=self.domain,
            tech_stack=tech
        )

        return Lead(
            id=str(self.id),
            first_name=self.first_name,
            last_name=self.last_name,
            company_name=self.company_name,
            domain=self.domain,
            email=self.email,
            email_status=EmailStatus(self.email_status) if self.email_status in EmailStatus._value2member_map_ else EmailStatus.UNKNOWN,
            confidence_score=self.confidence_score,
            company_info=company,
            research_summary=self.research_summary,
            generated_copy=copy,
            campaign_status=CampaignStatus(self.campaign_status) if self.campaign_status in CampaignStatus._value2member_map_ else CampaignStatus.NEW,
            metadata=meta
        )


def get_default_engine(db_url: Optional[str] = None):
    """Create SQLAlchemy engine defaulting to SQLite file storage."""
    if not db_url:
        data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = data_dir / "opensdr.db"
        db_url = f"sqlite:///{db_path}"

    connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}
    return create_engine(db_url, connect_args=connect_args)


_engine = None
_SessionFactory = None


def init_db(db_url: Optional[str] = None):
    """Initialize database tables and session maker."""
    global _engine, _SessionFactory
    _engine = get_default_engine(db_url)
    Base.metadata.create_all(bind=_engine)
    _SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database sessions."""
    global _SessionFactory
    if _SessionFactory is None:
        init_db()
    session = _SessionFactory()
    try:
        yield session
    finally:
        session.close()


def save_or_update_lead(session: Session, lead: Lead) -> LeadRecord:
    """Persist a new lead or update an existing lead record."""
    record = None
    if lead.id and str(lead.id).isdigit():
        record = session.query(LeadRecord).filter(LeadRecord.id == int(lead.id)).first()

    if not record:
        record = LeadRecord(
            first_name=lead.first_name,
            last_name=lead.last_name,
            company_name=lead.company_name,
            domain=lead.domain
        )
        session.add(record)

    record.email = lead.email
    record.email_status = lead.email_status.value
    record.confidence_score = lead.confidence_score
    record.research_summary = lead.research_summary
    record.campaign_status = lead.campaign_status.value
    record.generated_copy_json = json.dumps(lead.generated_copy or {})
    record.metadata_json = json.dumps(lead.metadata or {})

    if lead.company_info and lead.company_info.tech_stack:
        record.tech_stack_json = json.dumps(lead.company_info.tech_stack)

    session.commit()
    session.refresh(record)
    lead.id = str(record.id)
    return record


def list_leads(session: Session, limit: int = 100, offset: int = 0) -> List[Lead]:
    """Retrieve paginated leads from database."""
    records = session.query(LeadRecord).order_by(LeadRecord.id.desc()).offset(offset).limit(limit).all()
    return [r.to_pydantic() for r in records]
