from enum import Enum


class PayloadBrand(Enum):
    unknown = "0"
    other = "1"
    americanExpress = "2"
    capitalOne = "3"
    dhl = "4"
    docuSign = "5"
    dropbox = "6"
    facebook = "7"
    firstAmerican = "8"
    microsoft = "9"
    netflix = "10"
    scotiabank = "11"
    sendGrid = "12"
    stewartTitle = "13"
    tesco = "14"
    wellsFargo = "15"
    syrinxCloud = "16"
    adobe = "17"
    teams = "18"
    zoom = "19"
    unknownFutureValue = "20"

    @property
    def entity_type_name(self):
        return "microsoft.graph.PayloadBrand"
