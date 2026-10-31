import re
from typing import List, Set
from pydantic import BaseModel, Field

COMMON_SPAM_TRIGGERS: Set[str] = {
    "100% free", "guaranteed", "risk free", "act now", "cash bonus",
    "wire transfer", "double your income", "congratulations", "urgent",
    "no catch", "make money fast", "winner", "pure profit", "unlimited"
}


class DeliverabilityReport(BaseModel):
    """Deliverability safety audit for outbound sales messages."""
    score: float = Field(ge=0.0, le=1.0)
    is_safe: bool
    subject_word_count: int
    body_word_count: int
    flagged_words: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


def extract_spam_triggers(text: str) -> List[str]:
    """Identify flagged commercial spam trigger phrases within text."""
    lower_text = text.lower()
    found: List[str] = []
    for trigger in COMMON_SPAM_TRIGGERS:
        pattern = r"\b" + re.escape(trigger) + r"\b"
        if re.search(pattern, lower_text):
            found.append(trigger)
    return found


def audit_email_deliverability(subject: str, body: str) -> DeliverabilityReport:
    """Analyze subject and body for spam signals and deliverability risks."""
    subject_words = [w for w in subject.split() if w]
    body_words = [w for w in body.split() if w]

    flagged = extract_spam_triggers(f"{subject} {body}")
    recommendations: List[str] = []
    score = 1.0

    if len(subject_words) > 7:
        score -= 0.15
        recommendations.append("Shorten subject line to 3-6 words to maximize mobile open rates.")

    if len(body_words) > 150:
        score -= 0.20
        recommendations.append("Keep cold email body under 125 words for higher executive reply rates.")
    elif len(body_words) < 20:
        score -= 0.10
        recommendations.append("Email body is brief; provide more clear context on your value proposition.")

    if flagged:
        penalty = min(0.40, len(flagged) * 0.15)
        score -= penalty
        recommendations.append(f"Remove flagged spam keywords: {', '.join(flagged)}")

    final_score = max(0.0, round(score, 2))
    return DeliverabilityReport(
        score=final_score,
        is_safe=final_score >= 0.70,
        subject_word_count=len(subject_words),
        body_word_count=len(body_words),
        flagged_words=flagged,
        recommendations=recommendations
    )
