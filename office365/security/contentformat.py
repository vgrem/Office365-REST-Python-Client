from enum import Enum


class ContentFormat(Enum):
    text = "0"
    html = "1"
    markdown = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.ContentFormat"
