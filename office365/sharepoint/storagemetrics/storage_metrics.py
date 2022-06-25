from office365.sharepoint.base_entity import BaseEntity


class StorageMetrics(BaseEntity):
    """Specifies the storage-related metrics for list folders in the site"""

    @property
    def last_modified(self):
        """
        Last modified date for all the items under the corresponding folder.

        :rtype: int or None
        """
        return self.properties.get("LastModified", None)

    @property
    def total_file_count(self):
        """
        Aggregate number of files within the corresponding folder and its sub-folders.
        Excludes versions, list item attachments, and non-customized documents.

        :rtype: int or None
        """
        return self.properties.get("TotalFileCount", None)

    @property
    def total_file_stream_size(self):
        """
        Aggregate stream size in bytes for all files under the corresponding folder and its sub-folders.
        Excludes version, metadata, list item attachment, and non-customized document sizes.

        :rtype: int or None
        """
        return self.properties.get("TotalFileStreamSize", None)

    @property
    def total_size(self):
        """
        Aggregate of total sizes in bytes for all items under the corresponding folder and its sub-folders.
        Total size for a file/folder includes stream, version, and metadata sizes.

        :rtype: int or None
        """
        return self.properties.get("TotalSize", None)
