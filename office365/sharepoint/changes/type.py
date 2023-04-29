class ChangeType:
    """Enumeration of the possible types of changes."""

    def __init__(self):
        pass

    NoChange = "NoChange"
    """Indicates that no change has taken place."""

    Add = "Add"
    """Specifies that an object has been added within the scope of a list, site, site collection, or content database"""

    Update = "Update"
    """Specifies that an object has been modified within the scope of a list, site, site collection,
    or content database."""

    DeleteObject = "DeleteObject"
    """
    Specifies that an object has been deleted within the scope of a list, site, site collection, or content database
    """

    Rename = "Rename"
    """The leaf in a URL has been renamed."""

    MoveAway = "MoveAway"
    """Specifies that a non-leaf segment within a URL has been renamed. The object was moved away from the
    location within the site specified by the change."""

    MoveInto = "MoveInto"
    """Specifies that a non-leaf segment within a URL has been renamed. The object was moved into the location within
    the site specified by the change."""

    Restore = "Restore"
    """Specifies that an object (1) has restored from a backup or from the Recycle Bin"""

    RoleAdd = "RoleAdd"
    """Specifies that a role definition has been added."""

    RoleDelete = "RoleDelete"
    """Specifies that a role definition has been deleted."""

    RoleUpdate = "RoleUpdate"
    """Specifies that a role definition has been updated."""

    AssignmentAdd = "AssignmentAdd"
    """Specifies that a user has been given permissions to a list. The list MUST have different permissions from
    its parent."""

    AssignmentDelete = "AssignmentDelete"
    """Specifies that a user has lost permissions to a list. The list MUST have different permissions from its parent"""

    MemberAdd = "MemberAdd"
    """Specifies that a user has been added to a group."""

    MemberDelete = "MemberDelete"
    """Specifies that a user has been removed from a group."""

    SystemUpdate = "SystemUpdate"
    """Specifies that a change has been made to an item by using the protocol server method."""

    Navigation = "Navigation"
    """Specifies that a change in the navigation structure of a site collection has been made."""

    ScopeAdd = "ScopeAdd"
    """Specifies that a change in permissions scope has been made to break inheritance from the parent of an object """

    ScopeDelete = "ScopeDelete"
    """Specifies that a change in permissions scope has been made to revert back to inheriting permissions from
    the parent of an object"""

    ListContentTypeAdd = "ListContentTypeAdd"
    """Specifies that a list content type has been added."""

    ListContentTypeDelete = "ListContentTypeDelete"
    """Specifies that a list content type has been deleted."""

    Dirty = "Dirty"
    """Specifies that this item has a pending modification due to an operation on another item."""

    Activity = "Activity"
    """Specifies that an activity change as specified in section 3.2.5.462 has been made to the object """
