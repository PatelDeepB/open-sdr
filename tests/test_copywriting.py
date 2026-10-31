import pytest
from opensdr.copywriting.deliverability import audit_email_deliverability, extract_spam_triggers
from opensdr.copywriting.templates import render_template
from opensdr.copywriting.writer import CopywriterAgent
from opensdr.models import CampaignStatus, Company, Lead


def test_should_flag_spam_triggers():
    # Arrange
    text = "This is 100% free with a guaranteed cash bonus and act now offer."

    # Act
    triggers = extract_spam_triggers(text)

    # Assert
    assert "100% free" in triggers
    assert "guaranteed" in triggers
    assert "cash bonus" in triggers
    assert "act now" in triggers


def test_should_penalize_deliverability_score_on_spam_keywords():
    # Arrange
    subject = "Quick question"
    body = "Here is a 100% free offer that is guaranteed to win."

    # Act
    report = audit_email_deliverability(subject, body)

    # Assert
    assert report.is_safe is False
    assert report.score < 0.70
    assert len(report.flagged_words) >= 2


def test_should_render_template_variables_accurately():
    # Arrange
    vars_map = {
        "first_name": "Jordan",
        "company_name": "Acme Corp",
        "pain_point": "wasting hours on manual data entry",
        "icebreaker": "Loved your recent product showcase.",
        "sender_name": "Taylor"
    }

    # Act
    rendered = render_template("quick_question", vars_map)

    # Assert
    assert "quick question re: Acme Corp" == rendered["subject"]
    assert "Hi Jordan," in rendered["body"]
    assert "Loved your recent product showcase." in rendered["body"]
    assert "Taylor" in rendered["body"]


def test_should_generate_full_three_step_sequence_for_lead():
    # Arrange
    company = Company(
        name="Starlight Media",
        domain="starlight.io",
        tech_stack=["HubSpot CRM"]
    )
    lead = Lead(
        first_name="Samantha",
        last_name="Reed",
        company_name="Starlight Media",
        domain="starlight.io",
        company_info=company
    )
    agent = CopywriterAgent(sender_name="Danielle")

    # Act
    processed_lead = agent.process_lead(lead)

    # Assert
    assert processed_lead.campaign_status == CampaignStatus.COPY_GENERATED
    assert "initial_subject" in processed_lead.generated_copy
    assert "followup_subject" in processed_lead.generated_copy
    assert "breakup_subject" in processed_lead.generated_copy
    assert "HubSpot CRM" in processed_lead.generated_copy["initial_body"]
