from office365.sharepoint.base_entity import BaseEntity


class SPPolicyStoreProxy(BaseEntity):

    @property
    def entity_type_name(self):
        return "SP.CompliancePolicy.SPPolicyStoreProxy"
