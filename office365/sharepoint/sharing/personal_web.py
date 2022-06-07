from office365.sharepoint.base_entity import BaseEntity


class PersonalWeb(BaseEntity):
    """Microsoft.SharePoint.Client.Sharing.PersonalWeb namespace represents methods that apply to a Web site for
    individual users. Methods act on the users default document library."""

    @property
    def entity_type_name(self):
        return "SP.Sharing.PersonalWeb"
