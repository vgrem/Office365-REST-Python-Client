from office365.directory.users.activities.activity import UserActivity
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath


class ActivityHistoryItem(Entity):
    """
    Represents a history item for an activity in an app. User activities represent a single destination within
    your app; for example, a TV show, a document, or a current campaign in a video game.
    When a user engages with that activity, the engagement is captured as a history item that indicates
    the start and end time for that activity. As the user re-engages with that activity over time, multiple
    history items are recorded for a single user activity.
    """

    @property
    def activity(self):
        """NavigationProperty/Containment; navigation property to the associated activity."""
        return self.properties.get('activity',
                                   UserActivity(self.context, ResourcePath("activity", self.resource_path)))
