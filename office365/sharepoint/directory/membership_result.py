from office365.sharepoint.entity import Entity


class MembershipResult(Entity):
    @property
    def entity_type_name(self):
        return "SP.Directory.MembershipResult"
