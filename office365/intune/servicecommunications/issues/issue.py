from office365.intune.servicecommunications.announcement_base import ServiceAnnouncementBase


class ServiceHealthIssue(ServiceAnnouncementBase):
    """
    Represents a service health issue in a service.

    The service health issue can be a service incident or service advisory. For example:

       - Service incident: "Exchange mailbox service is down".
       - Service advisory: "Users may experience delays in emails reception".
    """


