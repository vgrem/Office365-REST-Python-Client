from office365.entity import Entity


class WorkbookApplication(Entity):
    """Represents the Excel application that manages the workbook."""

    @property
    def calculation_mode(self):
        """	Returns the calculation mode used in the workbook. Possible values are:
        Automatic, AutomaticExceptTables, Manual."""
        return self.properties.get("calculationMode", None)
