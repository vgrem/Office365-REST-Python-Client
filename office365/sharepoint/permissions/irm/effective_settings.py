from office365.sharepoint.base_entity import BaseEntity


class EffectiveInformationRightsManagementSettings(BaseEntity):
    """A collection of effective IRM settings on the file."""

    @property
    def allow_print(self):
        """
        Specifies whether a user can print the downloaded document.
        :rtype: bool
        """
        return self.properties.get("AllowPrint", None)

    @property
    def template_id(self):
        """
        Gets the template ID of the RMS template that will be applied to the file/library.
        :rtype: str or None
        """
        return self.properties.get("TemplateId", None)
