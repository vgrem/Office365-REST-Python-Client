from office365.runtime.client_value import ClientValue


class WorkbookWorksheetProtectionOptions(ClientValue):
    """Represents the protection of a sheet object."""

    def __init__(
        self, allowAutoFilter=None, allowDeleteColumns=None, allowDeleteRows=None
    ):
        self.allowAutoFilter = allowAutoFilter
        self.allowDeleteColumns = allowDeleteColumns
        self.allowDeleteRows = allowDeleteRows
