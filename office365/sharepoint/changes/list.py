from office365.sharepoint.changes.change import Change


class ChangeList(Change):

    @property
    def base_template(self):
        return self.properties.get("BaseTemplate", None)

    @property
    def list_id(self):
        return self.properties.get("ListId", None)
