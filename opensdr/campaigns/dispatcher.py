import abc
from typing import Dict, List, Optional
import httpx
from pydantic import BaseModel, Field


class InboxAccount(BaseModel):
    """Outbound email account with daily sending quotas."""
    email: str
    display_name: str
    daily_limit: int = 50
    sent_today: int = 0

    @property
    def has_capacity(self) -> bool:
        return self.sent_today < self.daily_limit


class InboxRotator:
    """Manages round-robin rotation across multiple sender accounts to preserve reputation."""

    def __init__(self, inboxes: List[InboxAccount]):
        if not inboxes:
            raise ValueError("InboxRotator requires at least one configured InboxAccount.")
        self.inboxes = inboxes
        self._current_index = 0

    def get_next_available_inbox(self) -> Optional[InboxAccount]:
        """Select the next inbox that has remaining daily capacity."""
        total = len(self.inboxes)
        for _ in range(total):
            inbox = self.inboxes[self._current_index]
            self._current_index = (self._current_index + 1) % total
            if inbox.has_capacity:
                return inbox
        return None


class BaseDispatcher(abc.ABC):
    """Abstract interface for dispatching outbound sales emails."""

    @abc.abstractmethod
    async def send_message(
        self,
        sender_inbox: InboxAccount,
        recipient_email: str,
        subject: str,
        body: str
    ) -> bool:
        """Send message and return True if successfully dispatched."""
        pass


class MockDispatcher(BaseDispatcher):
    """In-memory dispatcher for simulations, tests, and dry-run execution."""

    def __init__(self):
        self.dispatched_messages: List[Dict[str, str]] = []

    async def send_message(
        self,
        sender_inbox: InboxAccount,
        recipient_email: str,
        subject: str,
        body: str
    ) -> bool:
        if not sender_inbox.has_capacity:
            return False

        message = {
            "from": sender_inbox.email,
            "to": recipient_email,
            "subject": subject,
            "body": body
        }
        self.dispatched_messages.append(message)
        sender_inbox.sent_today += 1
        return True


class WebhookDispatcher(BaseDispatcher):
    """Dispatches outbound email payloads to a CRM or external webhook endpoint."""

    def __init__(self, webhook_url: str, timeout_seconds: float = 5.0):
        self.webhook_url = webhook_url
        self.timeout = timeout_seconds

    async def send_message(
        self,
        sender_inbox: InboxAccount,
        recipient_email: str,
        subject: str,
        body: str
    ) -> bool:
        if not sender_inbox.has_capacity:
            return False

        payload = {
            "from_email": sender_inbox.email,
            "to_email": recipient_email,
            "subject": subject,
            "body": body
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(self.webhook_url, json=payload)
                if res.status_code in (200, 201, 202):
                    sender_inbox.sent_today += 1
                    return True
                return False
        except Exception:
            return False
