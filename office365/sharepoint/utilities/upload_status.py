from office365.sharepoint.base_entity import BaseEntity


class UploadStatus(BaseEntity):
    """The status of a chunk session upload."""

    @property
    def expected_content_range(self):
        """The string representation of the byte offset of the stream uploaded in chunk upload session that the
        next ContinueUpload (3.2.5.64.2.1.17) call uses to continue chunk upload.

        :rtype: str or None
        """
        return self.properties.get('ExpectedContentRange', None)

    @property
    def expiration_date_time(self):
        """The earliest time at which the chunk upload session will be automatically expired and then deleted.

        :rtype: str or None
        """
        return self.properties.get('ExpirationDateTime', None)

    @property
    def upload_id(self):
        """Unique Id of the chunk session upload.

        :rtype: str or None
        """
        return self.properties.get('UploadId', None)

    @property
    def property_ref_name(self):
        return "ExpectedContentRange"

    @property
    def entity_type_name(self):
        return "SP.Utilities.UploadStatus"
