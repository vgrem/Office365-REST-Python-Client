from office365.runtime.client_value import ClientValue


class ComplianceTag(ClientValue):

    @property
    def entity_type_name(self):
        return "SP.CompliancePolicy.ComplianceTag"
