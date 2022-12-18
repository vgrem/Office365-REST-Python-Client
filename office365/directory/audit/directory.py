from office365.directory.audit.activity_initiator import AuditActivityInitiator
from office365.entity import Entity


class DirectoryAudit(Entity):
    """Represents the directory audit items and its collection."""

    @property
    def category(self):
        """
        Indicates which resource category that's targeted by the activity.
        For example: UserManagement, GroupManagement, ApplicationManagement, RoleManagement.
        """
        return self.properties.get("category", None)

    @property
    def initiated_by(self):
        """
        Indicates information about the user or app initiated the activity.
        """
        return self.properties.get("initiatedBy", AuditActivityInitiator())

    @property
    def operation_type(self):
        """
        Indicates the type of operation that was performed. The possible values include but are not limited
        to the following: Add, Assign, Update, Unassign, and Delete.
        """
        return self.properties.get("operationType", None)

    @property
    def logged_by_service(self):
        """
        Indicates information on which service initiated the activity. For example:
        Self-service Password Management, Core Directory, B2C, Invited Users, Microsoft Identity Manager,
        Privileged Identity Management.
        """
        return self.properties.get("loggedByService", None)
