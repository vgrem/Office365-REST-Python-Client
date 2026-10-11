from enum import Enum


class OAuthAppScope(Enum):
    unknown = "0"
    readCalendar = "1"
    readContact = "2"
    readMail = "3"
    readAllChat = "4"
    readAllFile = "5"
    readAndWriteMail = "6"
    sendMail = "7"
    unknownFutureValue = "8"

    @property
    def entity_type_name(self):
        return "microsoft.graph.OAuthAppScope"
