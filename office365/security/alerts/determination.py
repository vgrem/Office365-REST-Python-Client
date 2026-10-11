from enum import Enum


class AlertDetermination(Enum):
    unknown = "0"
    apt = "10"
    malware = "20"
    securityPersonnel = "30"
    securityTesting = "40"
    unwantedSoftware = "50"
    other = "60"
    multiStagedAttack = "70"
    compromisedAccount = "80"
    phishing = "90"
    maliciousUserActivity = "100"
    notMalicious = "110"
    notEnoughDataToValidate = "120"
    confirmedActivity = "130"
    lineOfBusinessApplication = "140"
    unknownFutureValue = "149"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.AlertDetermination"
