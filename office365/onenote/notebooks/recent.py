from office365.onenote.notebooks.recent_links import RecentNotebookLinks
from office365.runtime.client_value import ClientValue


class RecentNotebook(ClientValue):
    """A recently accessed OneNote notebook. A recentNotebook is similar to a notebook but has fewer properties."""

    def __init__(
        self,
        display_name=None,
        last_accessed_time=None,
        links=RecentNotebookLinks(),
        source_service=None,
    ):
        """
        :param str display_name: The name of the notebook.
        :param RecentNotebookLinks links: Links for opening the notebook.
            The oneNoteClientURL link opens the notebook in the OneNote client, if it's installed.
            The oneNoteWebURL link opens the notebook in OneNote on the web.
        """
        self.displayName = display_name
        self.lastAccessedTime = last_accessed_time
        self.links = links
        self.sourceService = source_service
