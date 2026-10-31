import enum
import re
from typing import Optional
from pydantic import BaseModel, Field


class ReplyIntent(str, enum.Enum):
    """Categorized behavioral intent of an incoming prospect reply."""
    INTERESTED = "interested"
    OBJECTION = "objection"
    WRONG_PERSON = "wrong_person"
    OUT_OF_OFFICE = "out_of_office"
    UNSUBSCRIBE = "unsubscribe"
    NEUTRAL = "neutral"


class InboundAnalysis(BaseModel):
    """Structured understanding of an inbound email response."""
    intent: ReplyIntent
    confidence: float = Field(ge=0.0, le=1.0)
    referral_email: Optional[str] = None
    referral_name: Optional[str] = None
    suggested_action: str
    original_text_snippet: str


UNSUBSCRIBE_PATTERNS = [
    r"\bunsubscribe\b", r"\bremove me\b", r"\bstop emailing\b",
    r"\bnot interested\b", r"\bdo not contact\b", r"\btake me off\b"
]

OUT_OF_OFFICE_PATTERNS = [
    r"\bout of the office\b", r"\bauto-reply\b", r"\bautomated response\b",
    r"\bon vacation\b", r"\bwill be returning\b", r"\baway from my desk\b"
]

INTERESTED_PATTERNS = [
    r"\bsounds good\b", r"\blet'?s chat\b", r"\bsend over\b",
    r"\bopen to a call\b", r"\bcalendar\b", r"\btalk next week\b",
    r"\bwhat does pricing\b", r"\bmore details\b", r"\bdemo\b",
    r"\binterested\b", r"\bfree on\b", r"\bavailable\b"
]

REFERRAL_PATTERNS = [
    r"\bnot the right person\b", r"\breach out to\b", r"\bspeak with\b",
    r"\bcontact\b", r"\btry emailing\b", r"\bpassed this to\b"
]


def extract_referral_email(text: str) -> Optional[str]:
    """Scan response text for referral email addresses provided by prospect."""
    matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return matches[0] if matches else None


def classify_inbound_reply(reply_text: str) -> InboundAnalysis:
    """Analyze incoming email text and determine exact intent category."""
    if not reply_text:
        return InboundAnalysis(
            intent=ReplyIntent.NEUTRAL,
            confidence=0.5,
            suggested_action="Review manually",
            original_text_snippet=""
        )

    lower_text = reply_text.strip().lower()

    # 1. Check for immediate unsubscribe / opt-out
    for pattern in UNSUBSCRIBE_PATTERNS:
        if re.search(pattern, lower_text):
            return InboundAnalysis(
                intent=ReplyIntent.UNSUBSCRIBE,
                confidence=0.98,
                suggested_action="Immediately halt follow-ups and add to suppression list",
                original_text_snippet=reply_text[:120]
            )

    # 2. Check for Out-of-Office automated responses
    for pattern in OUT_OF_OFFICE_PATTERNS:
        if re.search(pattern, lower_text):
            return InboundAnalysis(
                intent=ReplyIntent.OUT_OF_OFFICE,
                confidence=0.95,
                suggested_action="Pause campaign sequence until prospect returns",
                original_text_snippet=reply_text[:120]
            )

    # 3. Check for referral to a different colleague
    for pattern in REFERRAL_PATTERNS:
        if re.search(pattern, lower_text):
            referral = extract_referral_email(reply_text)
            return InboundAnalysis(
                intent=ReplyIntent.WRONG_PERSON,
                confidence=0.90,
                referral_email=referral,
                suggested_action=f"Thank original contact and create new lead for referral: {referral or 'Colleague'}",
                original_text_snippet=reply_text[:120]
            )

    # 4. Check for positive interest signals
    for pattern in INTERESTED_PATTERNS:
        if re.search(pattern, lower_text):
            return InboundAnalysis(
                intent=ReplyIntent.INTERESTED,
                confidence=0.92,
                suggested_action="Send calendar link and schedule discovery meeting",
                original_text_snippet=reply_text[:120]
            )

    # Default fallback
    return InboundAnalysis(
        intent=ReplyIntent.NEUTRAL,
        confidence=0.60,
        suggested_action="Review reply manually or send general inquiry follow-up",
        original_text_snippet=reply_text[:120]
    )
