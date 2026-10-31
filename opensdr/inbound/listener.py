import email
import imaplib
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from opensdr.campaigns.dispatcher import BaseDispatcher, MockDispatcher
from opensdr.db import LeadRecord, save_or_update_lead
from opensdr.inbound.agent import InboundActionResponse, InboundSDRAgent


class ImapConfig(BaseModel):
    """Configuration credentials for an IMAP mailbox connection."""
    host: str
    port: int = 993
    username: str
    password: str
    use_ssl: bool = True


class ImapInboxListener:
    """Listens for new prospect replies via IMAP and triggers autonomous SDR actions."""

    def __init__(
        self,
        config: Optional[ImapConfig] = None,
        booking_url: str = "https://cal.com/team/15min",
        dispatcher: Optional[BaseDispatcher] = None
    ):
        self.config = config
        self.booking_url = booking_url
        self.agent = InboundSDRAgent(booking_url=booking_url)
        self.dispatcher = dispatcher or MockDispatcher()

    def sync_replies_for_session(
        self,
        session: Session,
        incoming_messages: Optional[List[dict]] = None
    ) -> List[InboundActionResponse]:
        """Process incoming messages against database leads and execute SDR actions."""
        messages = incoming_messages or self._fetch_unread_imap_messages()
        actions: List[InboundActionResponse] = []

        for msg in messages:
            sender_email = msg.get("from_email", "").strip().lower()
            body_text = msg.get("body", "")

            lead_record = session.query(LeadRecord).filter(
                LeadRecord.email.ilike(sender_email)
            ).first()

            if not lead_record:
                continue

            lead = lead_record.to_pydantic()
            action = self.agent.process_reply(lead, body_text)
            save_or_update_lead(session, lead)
            actions.append(action)

        return actions

    def _fetch_unread_imap_messages(self) -> List[dict]:
        """Fetch unread messages from IMAP server if credentials are configured."""
        if not self.config:
            return []

        messages: List[dict] = []
        try:
            mail = imaplib.IMAP4_SSL(self.config.host, self.config.port)
            mail.login(self.config.username, self.config.password)
            mail.select("INBOX")

            _, data = mail.search(None, "UNSEEN")
            mail_ids = data[0].split()

            for num in mail_ids[-20:]:  # Process up to 20 most recent
                _, msg_data = mail.fetch(num, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        from_addr = email.utils.parseaddr(msg["From"])[1]
                        subject = msg.get("Subject", "")
                        body = self._extract_email_body(msg)
                        messages.append({
                            "from_email": from_addr,
                            "subject": subject,
                            "body": body
                        })

            mail.close()
            mail.logout()
            return messages
        except Exception:
            return []

    def _extract_email_body(self, msg: email.message.Message) -> str:
        """Extract plain text from multipart email message."""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode(errors="ignore")
        return msg.get_payload(decode=True).decode(errors="ignore") if msg.get_payload() else ""
