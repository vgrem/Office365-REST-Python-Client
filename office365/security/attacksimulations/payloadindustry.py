from enum import Enum


class PayloadIndustry(Enum):
    unknown = "0"
    other = "1"
    banking = "2"
    businessServices = "3"
    consumerServices = "4"
    education = "5"
    energy = "6"
    construction = "7"
    consulting = "8"
    financialServices = "9"
    government = "10"
    hospitality = "11"
    insurance = "12"
    legal = "13"
    courierServices = "14"
    IT = "15"
    healthcare = "16"
    manufacturing = "17"
    retail = "18"
    telecom = "19"
    realEstate = "20"
    unknownFutureValue = "21"

    @property
    def entity_type_name(self):
        return "microsoft.graph.PayloadIndustry"
