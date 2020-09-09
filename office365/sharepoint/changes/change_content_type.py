from office365.sharepoint.changes.change import Change


class ChangeContentType(Change):
    """Specifies a change on a content type."""

    @property
    def content_type_id(self):
        return self.properties.get("ContentTypeId", None)
