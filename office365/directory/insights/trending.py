from office365.entity import Entity


class Trending(Entity):
    """
    Rich relationship connecting a user to documents that are trending around the user (are relevant to the user).
    OneDrive files, and files stored on SharePoint team sites can trend around the user.
    """
