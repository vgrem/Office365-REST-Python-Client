from office365.sharepoint.changes.change import Change


class ChangeGroup(Change):

    @property
    def group_id(self):
        return self.properties.get("GroupId", None)
