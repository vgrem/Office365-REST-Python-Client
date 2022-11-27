from office365.runtime.client_value import ClientValue


class SPHSiteReference(ClientValue):

    @property
    def entity_type_name(self):
        return "SP.SPHSiteReference"
