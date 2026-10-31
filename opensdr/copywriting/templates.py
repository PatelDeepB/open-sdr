from typing import Dict
from pydantic import BaseModel


class EmailTemplate(BaseModel):
    """Specification for an outreach email template."""
    name: str
    subject_pattern: str
    body_pattern: str


TEMPLATES: Dict[str, EmailTemplate] = {
    "quick_question": EmailTemplate(
        name="quick_question",
        subject_pattern="quick question re: {company_name}",
        body_pattern=(
            "Hi {first_name},\n\n"
            "{icebreaker}\n\n"
            "We help growth teams solve {pain_point}.\n\n"
            "Open to exploring a brief 5-minute chat next week?\n\n"
            "Best,\n{sender_name}"
        )
    ),
    "pas": EmailTemplate(
        name="problem_agitate_solution",
        subject_pattern="{company_name}'s outbound pipeline",
        body_pattern=(
            "Hi {first_name},\n\n"
            "{icebreaker}\n\n"
            "A common bottleneck at {company_name} is {pain_point}.\n\n"
            "We automated this workflow end-to-end to cut manual SDR overhead by 70%.\n\n"
            "Worth a quick look this Thursday?\n\n"
            "Cheers,\n{sender_name}"
        )
    ),
    "followup_bump": EmailTemplate(
        name="followup_bump",
        subject_pattern="re: {original_subject}",
        body_pattern=(
            "Hi {first_name},\n\n"
            "Bumping this to the top of your inbox in case it slipped past.\n\n"
            "Did you have a chance to review the note below?\n\n"
            "Best,\n{sender_name}"
        )
    ),
    "breakup": EmailTemplate(
        name="breakup_email",
        subject_pattern="closing loop re: {company_name}",
        body_pattern=(
            "Hi {first_name},\n\n"
            "Assuming this is not a focus area right now, so I will pause my outreach.\n\n"
            "If your priorities shift later, feel free to reach back out.\n\n"
            "Best regards,\n{sender_name}"
        )
    )
}


def render_template(template_name: str, variables: Dict[str, str]) -> Dict[str, str]:
    """Render subject and body with provided dynamic personalization variables."""
    template = TEMPLATES.get(template_name)
    if not template:
        raise ValueError(f"Unknown template: '{template_name}'")

    subject = template.subject_pattern.format(**variables)
    body = template.body_pattern.format(**variables)
    return {
        "subject": subject,
        "body": body
    }
