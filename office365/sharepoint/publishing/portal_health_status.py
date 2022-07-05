from office365.runtime.client_value import ClientValue


class PortalHealthStatus(ClientValue):

    def __init__(self, status=None):
        """
        :param int status:
        """
        self.Status = status

