from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.admin.exchange.exchange_message_trace_status import (
        ExchangeMessageTraceStatus,
    )


class ExchangeMessageTrace(Entity):
    @property
    def from_ip(self) -> Optional[str]:
        """Gets the fromIP property"""
        return self.properties.get("fromIP", None)

    @property
    def message_id(self) -> Optional[str]:
        """Gets the messageId property"""
        return self.properties.get("messageId", None)

    @property
    def received_date_time(self) -> datetime:
        """Gets the receivedDateTime property"""
        return self.properties.get("receivedDateTime", datetime.min)

    @property
    def recipient_address(self) -> Optional[str]:
        """Gets the recipientAddress property"""
        return self.properties.get("recipientAddress", None)

    @property
    def sender_address(self) -> Optional[str]:
        """Gets the senderAddress property"""
        return self.properties.get("senderAddress", None)

    @property
    def size(self) -> Optional[int]:
        """Gets the size property"""
        return self.properties.get("size", None)

    @property
    def subject(self) -> Optional[str]:
        """Gets the subject property"""
        return self.properties.get("subject", None)

    @property
    def to_ip(self) -> Optional[str]:
        """Gets the toIP property"""
        return self.properties.get("toIP", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ExchangeMessageTrace"

    @property
    def status(self) -> ExchangeMessageTraceStatus:
        """Gets the status property"""
        from office365.admin.exchange.exchange_message_trace_status import (
            ExchangeMessageTraceStatus,
        )

        return self.properties.get("status", ExchangeMessageTraceStatus.gettingStatus)
