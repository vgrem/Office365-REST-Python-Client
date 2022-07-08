from office365.entity import Entity
from office365.onedrive.workbooks.ranges.format_protection import WorkbookFormatProtection
from office365.runtime.paths.resource_path import ResourcePath


class WorkbookRangeFormat(Entity):
    """A format object encapsulating the range's font, fill, borders, alignment, and other properties."""

    @property
    def protection(self):
        """Returns the format protection object for a range """
        return self.properties.get('protection',
                                   WorkbookFormatProtection(self.context,
                                                            ResourcePath("protection", self.resource_path)))
