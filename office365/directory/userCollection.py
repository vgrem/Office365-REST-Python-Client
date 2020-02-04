from office365.directory.user import User
from office365.directory.directoryObjectCollection import DirectoryObjectCollection


class UserCollection(DirectoryObjectCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(UserCollection, self).__init__(context, User, resource_path)

