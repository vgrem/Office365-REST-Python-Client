class PageType:

    def __init__(self):
        """As specified in [MS-WSSFO3] section 2.2.1.2.14."""
        pass

    Invalid = -1
    """Specifies a page that does not correspond to a list view or a list form."""

    DefaultView = 0
    """Specifies a page that is the default view for a list."""

    NormalView = 1
    """Specifies a page that is a list view and is not the default view for a list."""

    DialogView = 2
    """Specifies a page that can be displayed within a dialog box on a client computer."""

    View = 3
    """Specifies a page that is a list view."""

    DisplayForm = 4

    DisplayFormDialog = 5

    EditForm = 6

    EditFormDialog = 7

    NewForm = 8

    NewFormDialog = 9

    SolutionForm = 10

    PAGE_MAXITEMS = 11
