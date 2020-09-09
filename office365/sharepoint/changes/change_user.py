from office365.sharepoint.changes.change import Change


class ChangeUser(Change):

    @property
    def user_id(self):
        return self.properties.get("UserId", None)
