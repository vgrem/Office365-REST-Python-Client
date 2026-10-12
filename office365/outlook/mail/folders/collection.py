from office365.delta_collection import DeltaCollection
from office365.directory.permissions.require_permission import require_permission
from office365.outlook.mail.folders.folder import MailFolder
from office365.runtime.odata.literals import escape_odata_string


class MailFolderCollection(DeltaCollection[MailFolder]):
    """Mail folder's collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, MailFolder, resource_path)

    def find_by_display_name(self, display_name: str, *, required: bool = False) -> MailFolder:
        """Look up a mail folder by its ``displayName``.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        folder matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            display_name (str): The folder display name
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"displayName eq '{escape_odata_string(display_name)}'", required=required)

    @require_permission(delegated=["Mail.ReadWrite"], application=["Mail.ReadWrite"])
    def add(self, display_name: str, is_hidden: bool = False) -> MailFolder:
        """
        Use this API to create a new mail folder in the root folder of the user's mailbox.

        If you intend a new folder to be hidden, you must set the isHidden property to true on creation.
        """
        props = {"displayName": display_name, "isHidden": is_hidden}
        return super().add(**props)
