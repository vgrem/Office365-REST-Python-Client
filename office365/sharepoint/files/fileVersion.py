from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import DeleteEntityQuery


class FileVersion(ClientObject):
    """Represents a version of a File object."""

    @property
    def url(self):
        """Gets a value that specifies the relative URL of the file version based on the URL for the site or subsite."""
        if self.is_property_available('Url'):
            return self.properties["Url"]
        else:
            return None

    @property
    def versionLabel(self):
        """Gets a value that specifies the implementation specific identifier of the file."""
        if self.is_property_available('VersionLabel'):
            return self.properties["VersionLabel"]
        else:
            return None

    @property
    def isCurrentVersion(self):
        """Gets a value that specifies whether the file version is the current version."""
        if self.is_property_available('IsCurrentVersion'):
            return self.properties["IsCurrentVersion"]
        else:
            return None

    @property
    def checkInComment(self):
        """Gets a value that specifies the check-in comment."""
        if self.is_property_available('CheckInComment'):
            return self.properties["CheckInComment"]
        else:
            return None

    def delete_object(self):
        """Deletes the fields."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
