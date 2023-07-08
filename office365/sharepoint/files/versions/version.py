from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity import BaseEntity
from office365.runtime.paths.key import KeyPath


class FileVersion(BaseEntity):
    """Represents a version of a File object."""

    def download(self, file_object):
        """Downloads the file version as a stream and save into a file.

        :type file_object: typing.IO
        """
        def _file_version_loaded():
            def _save_file(return_type):
                """
                :type return_type:ClientResult
                """
                file_object.write(return_type.value)
            self.open_binary_stream().after_execute(_save_file)

        self.ensure_property("ID", _file_version_loaded)
        return self

    def open_binary_stream(self):
        """Opens the file as a stream."""
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "OpenBinaryStream", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def open_binary_stream_with_options(self, open_options):
        """Opens the file as a stream."""
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "OpenBinaryStreamWithOptions", [open_options], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def created_by(self):
        """Gets the user that created the file version."""
        from office365.sharepoint.principal.users.user import User
        return self.properties.get("CreatedBy", User(self.context, ResourcePath("CreatedBy", self.resource_path)))

    @property
    def id(self):
        """Gets a file version identifier"""
        return int(self.properties.get("ID", -1))

    @property
    def url(self):
        """Gets a value that specifies the relative URL of the file version based on the URL for the site or subsite."""
        return self.properties.get("Url", None)

    @property
    def version_label(self):
        """Gets a value that specifies the implementation specific identifier of the file."""
        return self.properties.get("VersionLabel", None)

    @property
    def is_current_version(self):
        """Gets a value that specifies whether the file version is the current version."""
        return self.properties.get("IsCurrentVersion", None)

    @property
    def checkin_comment(self):
        """Gets a value that specifies the check-in comment.

        :rtype: str or None
        """
        return self.properties.get("CheckInComment", None)

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "CreatedBy": self.created_by,
            }
            default_value = property_mapping.get(name, None)
        return super(FileVersion, self).get_property(name, default_value)

    def set_property(self, key, value, persist_changes=True):
        super(FileVersion, self).set_property(key, value, persist_changes)
        if self._resource_path is None:
            if key == "ID":
                self._resource_path = KeyPath(value, self.parent_collection.resource_path)
        return self
