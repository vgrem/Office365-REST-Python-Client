from office365.entity import Entity


class MessageRule(Entity):
    """A rule that applies to messages in the Inbox of a user.

    In Outlook, you can set up rules for incoming messages in the Inbox to carry out specific internal
    upon certain conditions."""

    @property
    def is_read_only(self):
        """
        Indicates if the rule is read-only and cannot be modified or deleted by the rules REST API.
        """
        return self.properties.get("isReadOnly", None)
