from typing import Optional

from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity


class ItemRetentionLabel(Entity):
    """
    Groups retention and compliance-related properties on an item into a single structure.
    Currently, supported only for driveItem.
    """

    @property
    def is_label_applied_explicitly(self):
        # type: () -> Optional[bool]
        """Specifies whether the label is applied explicitly on the item.
        True indicates that the label is applied explicitly; otherwise, the label is inherited from its parent.
        Read-only."""
        return self.properties.get("isLabelAppliedExplicitly", None)

    @property
    def label_applied_by(self):
        # type: () -> Optional[IdentitySet]
        """Identity of the user who applied the label. Read-only."""
        return self.properties.get("labelAppliedBy", IdentitySet())
