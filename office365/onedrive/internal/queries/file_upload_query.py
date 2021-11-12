from office365.onedrive.internal.queries.upload_session_query import UploadSessionQuery
from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.driveitems.drive_item_uploadable_properties import DriveItemUploadableProperties
from office365.onedrive.internal.paths.resource_path_url import ResourcePathUrl


class ResumableFileUpload(UploadSessionQuery):
    """Create an upload session to allow your app to upload files up to the maximum file size. An upload session
    allows your app to upload ranges of the file in sequential API requests, which allows the transfer to be resumed
    if a connection is dropped while the upload is in progress. """

    def create_upload_session(self):
        item = DriveItemUploadableProperties()
        item.name = self.file_name
        return self.binding_type.create_upload_session(item)

    @property
    def binding_type(self):
        return DriveItem(self.context, ResourcePathUrl(self.file_name, self._binding_type.resource_path))

    @property
    def return_type(self):
        if self._return_type is None:
            self._return_type = DriveItem(self.context,
                                          ResourcePathUrl(self.file_name, self._binding_type.resource_path))
        return self._return_type
