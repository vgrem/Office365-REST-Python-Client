from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.security.alerts.emailrole import EmailRole
from office365.security.alerts.logontype import LogonType
from office365.security.alerts.useraccountsecuritytype import (
    UserAccountSecurityType,
)


@dataclass
class UserSecurityState(ClientValue):
    aadUserId: str | None = None
    accountName: str | None = None
    domainName: str | None = None
    emailRole: EmailRole = EmailRole.unknown
    isVpn: bool | None = None
    logonDateTime: datetime | None = None
    logonId: str | None = None
    logonIp: str | None = None
    logonLocation: str | None = None
    logonType: LogonType = LogonType.unknown
    onPremisesSecurityIdentifier: str | None = None
    riskScore: str | None = None
    userAccountType: UserAccountSecurityType = UserAccountSecurityType.unknown
    userPrincipalName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserSecurityState"
