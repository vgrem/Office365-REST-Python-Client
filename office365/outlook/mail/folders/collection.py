from office365.delta_collection import DeltaCollection
from office365.outlook.mail.folders.folder import MailFolder


class MailFolderCollection(DeltaCollection):

    def __init__(self, context, resource_path=None):
        super(MailFolderCollection, self).__init__(context, MailFolder, resource_path)

    def __getitem__(self, key):
        """
        :param str key: MailFolder identifier or display name
        :rtype: MailFolder
        """
        return super(MailFolderCollection, self).__getitem__(key)
