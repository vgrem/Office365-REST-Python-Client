from office365.runtime.client_object import ClientObject
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class UserProfile(ClientObject):

    def create_personal_site_enque(self, isInteractive):
        """
        Enqueues creating a personal site for this user, which can be used to share documents, web pages,
            and other files.

        :type isInteractive: bool
        """
        payload = {"isInteractive": isInteractive}
        qry = ServiceOperationQuery(self, "CreatePersonalSiteEnque", None, payload, None, None)
        self.context.add_query(qry)
        return self
