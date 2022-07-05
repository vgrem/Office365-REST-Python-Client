from office365.sharepoint.base_entity import BaseEntity


class TranslationJobStatus(BaseEntity):
    """The TranslationJobStatus type is used to get information about previously submitted translation jobs and
    the translation items associated with them. The type provides methods to retrieve
    TranslationJobInfo (section 3.1.5.4) and TranslationItemInfo (section 3.1.5.2) objects."""

    @property
    def entity_type_name(self):
        return "SP.Translation.TranslationJobStatus"
