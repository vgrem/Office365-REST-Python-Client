import datetime
from typing import Optional

from office365.directory.audit.activity_initiator import AuditActivityInitiator
from office365.entity import Entity


class DirectoryAudit(Entity):
    """Represents the directory audit items and its collection."""

    def __repr__(self):
        return self.activity_display_name or self.entity_type_name

    @property
    def activity_datetime(self):
        """Indicates the date and time the activity was performed."""
        return self.properties.get("activityDateTime", datetime.datetime.min)

    @property
    def activity_display_name(self):
        # type: () -> Optional[str]
        """
        Indicates the activity name or the operation name (examples: "Create User" and "Add member to group").
        For a list of activities logged, refer to Azure AD audit log categories and activities.
        """
        return self.properties.get("activityDisplayName", None)

    @property
    def category(self):
        # type: () -> Optional[str]
        """
        Indicates which resource category that's targeted by the activity.
        For example: UserManagement, GroupManagement, ApplicationManagement, RoleManagement.
        """
        return self.properties.get("category", None)

    @property
    def correlation_id(self):
        # type: () -> Optional[str]
        """
        Indicates a unique ID that helps correlate activities that span across various services.
        Can be used to trace logs across services.
        """
        return self.properties.get("correlationId", None)

    @property
    def initiated_by(self):
        """
        Indicates information about the user or app initiated the activity.
        """
        return self.properties.get("initiatedBy", AuditActivityInitiator())

    @property
    def operation_type(self):
        # type: () -> Optional[str]
        """
        Indicates the type of operation that was performed. The possible values include but are not limited
        to the following: Add, Assign, Update, Unassign, and Delete.
        """
        return self.properties.get("operationType", None)

    @property
    def logged_by_service(self):
        # type: () -> Optional[str]
        """
        Indicates information on which service initiated the activity. For example:
        Self-service Password Management, Core Directory, B2C, Invited Users, Microsoft Identity Manager,
        Privileged Identity Management.
        """
        return self.properties.get("loggedByService", None)

    @property
    def result_reason(self):
        # type: () -> Optional[str]
        """
        Indicates the reason for failure if the result is failure or timeout.
        """
        return self.properties.get("resultReason", None)

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "activityDateTime": self.activity_datetime,
                "initiatedBy": self.initiated_by,
            }
            default_value = property_mapping.get(name, None)
        return super(DirectoryAudit, self).get_property(name, default_value)
