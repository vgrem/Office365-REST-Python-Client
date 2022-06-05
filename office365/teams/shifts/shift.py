from office365.teams.shifts.change_tracked_entity import ChangeTrackedEntity
from office365.teams.shifts.shift_item import ShiftItem


class Shift(ChangeTrackedEntity):
    """
    Represents a unit of scheduled work in a shifts.
    """

    @property
    def draft_shift(self):
        """The draft version of this shift that is viewable by managers.

        :rtype: ShiftItem
        """
        return self.get_property('draftShift', ShiftItem())

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "draftShift": self.draft_shift,
            }
            default_value = property_mapping.get(name, None)
        return super(Shift, self).get_property(name, default_value)
