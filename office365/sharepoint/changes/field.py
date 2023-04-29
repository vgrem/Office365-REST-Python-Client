from office365.sharepoint.changes.change import Change


class ChangeField(Change):
    """Specifies a change on a field"""

    @property
    def field_id(self):
        """"
        Identifies the changed field

        :rtype: str or None
        """
        return self.properties.get("FieldId", None)
