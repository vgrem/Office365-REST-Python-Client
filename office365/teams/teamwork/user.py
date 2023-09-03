from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.teams.apps.user_scope_installation import UserScopeTeamsAppInstallation


class UserTeamwork(Entity):
    """A container for the range of Microsoft Teams functionalities that are available per user in the tenant."""

    @property
    def installed_apps(self):
        """
        The apps installed in the personal scope of this user.
        """
        return self.properties.get('installedApps',
                                   EntityCollection(self.context, UserScopeTeamsAppInstallation,
                                                    ResourcePath("installedApps", self.resource_path)))

    def send_activity_notification(self, topic, activity_type, chain_id, preview_text, template_parameters=None):
        """
        Send an activity feed notification in the scope of a team. For more details about sending notifications
        and the requirements for doing so, see sending Teams activity notifications.

        :param TeamworkActivityTopic topic: Topic of the notification. Specifies the resource being talked about.
        :param str activity_type: Activity type. This must be declared in the Teams app manifest.
        :param int chain_id: Optional. Used to override a previous notification. Use the same chainId in subsequent
            requests to override the previous notification.
        :param ItemBody preview_text: Preview text for the notification. Microsoft Teams will only show first
            150 characters.
        :param dict template_parameters: Values for template variables defined in the activity feed entry corresponding
            to activityType in Teams app manifest.
        """
        payload = {
            "topic": topic,
            "activityType": activity_type,
            "chainId": chain_id,
            "previewText": preview_text,
            "templateParameters": template_parameters,
        }
        qry = ServiceOperationQuery(self, "sendActivityNotification", None, payload)
        self.context.add_query(qry)
        return self

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "installedApps": self.installed_apps
            }
            default_value = property_mapping.get(name, None)
        return super(UserTeamwork, self).get_property(name, default_value)
