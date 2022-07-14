from office365.runtime.client_value import ClientValue


class MenuNode(ClientValue):
    """Represents a navigation node in the navigation hierarchy. A navigation hierarchy is a tree structure of
    navigation nodes."""

    def __init__(self, current_lcid=None, title=None):
        """
        :param int current_lcid:
        :param str title: Specifies the title of the navigation node. The value is in the preferred language of the
            user, if available, or is in the default language of the site (2) as a fallback.
        """
        self.CurrentLCID = current_lcid
        self.Title = title
