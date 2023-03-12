from office365.entity import Entity


class SharedInsight(Entity):
    """
    An insight representing files shared with or by a specific user. The following shared files are supported:

      Files attached directly in an email or a meeting invite.
      OneDrive for Business and SharePoint modern attachments - files stored in OneDrive for Business and SharePoint
      that users share as a links in an email.
    """
