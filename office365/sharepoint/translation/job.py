from office365.sharepoint.base_entity import BaseEntity


class TranslationJob(BaseEntity):
    """
    The TranslationJob type is used to create new translation jobs.
    """

    @property
    def entity_type_name(self):
        return "SP.Translation.TranslationJob"
