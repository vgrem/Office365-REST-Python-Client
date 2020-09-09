from office365.sharepoint.changes.change import Change


class ChangeField(Change):

    @property
    def field_id(self):
        return self.properties.get("FieldId", None)
