from office365.runtime.client_value import ClientValue


class ComplianceTagInfo(ClientValue):

    @property
    def entity_type_name(self):
        return "SP.ComplianceFoundation.Models.ComplianceTagInfo"
