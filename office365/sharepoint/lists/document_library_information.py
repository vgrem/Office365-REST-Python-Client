from office365.runtime.client_value import ClientValue


class DocumentLibraryInformation(ClientValue):
    """Specifies the information for a document library on a site (2)."""

    @property
    def title(self):
        """Identifies the title of the document library."""
        return self.get_property("Title")
