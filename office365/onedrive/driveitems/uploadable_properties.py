from __future__ import annotations

from dataclasses import dataclass, field

from office365.onedrive.driveitems.source import DriveItemSource
from office365.onedrive.files.system_info import FileSystemInfo
from office365.onedrive.media_source import MediaSource
from office365.runtime.client_value import ClientValue
from office365.runtime.types.odata_property import odata


@dataclass
class DriveItemUploadableProperties(ClientValue):
    """The driveItemUploadableProperties resource represents an item being uploaded when creating an upload session."""

    fileSystemInfo: FileSystemInfo | None = field(default_factory=FileSystemInfo)
    name: str | None = None
    description: str | None = None
    _fileSize: int | None = None
    # Service-filled sources: read from a driveItem, never sent with one.
    driveItemSource: DriveItemSource = field(
        default_factory=DriveItemSource, metadata=odata(name="driveItemSource", readonly=True)
    )
    fileSize: int | None = None
    mediaSource: MediaSource = field(default_factory=MediaSource, metadata=odata(name="mediaSource", readonly=True))

    @property
    def file_size(self):
        """Provides an expected file size to perform a quota check prior to upload. Only on OneDrive Personal."""
        return self._fileSize

    @property
    def entity_type_name(self) -> str:
        return None  # type: ignore
