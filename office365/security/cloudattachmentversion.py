from enum import Enum


class CloudAttachmentVersion(Enum):
    latest = "1"
    recent10 = "2"
    recent100 = "3"
    all = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.CloudAttachmentVersion"
