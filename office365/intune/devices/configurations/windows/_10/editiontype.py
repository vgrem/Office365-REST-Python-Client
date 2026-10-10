from enum import Enum


class Windows10EditionType(Enum):
    windows10Enterprise = "0"
    windows10EnterpriseN = "1"
    windows10Education = "2"
    windows10EducationN = "3"
    windows10MobileEnterprise = "4"
    windows10HolographicEnterprise = "5"
    windows10Professional = "6"
    windows10ProfessionalN = "7"
    windows10ProfessionalEducation = "8"
    windows10ProfessionalEducationN = "9"
    windows10ProfessionalWorkstation = "10"
    windows10ProfessionalWorkstationN = "11"

    @property
    def entity_type_name(self):
        return "microsoft.graph.Windows10EditionType"
