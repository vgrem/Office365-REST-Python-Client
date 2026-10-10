from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class OutOfBoxFontPackageSettings(Entity):
    """"""

    @staticmethod
    def get_hide_out_of_box_font_packages(context: ClientContext) -> ClientResult[bool]:
        """GetHideOutOfBoxFontPackages operation."""
        from office365.sharepoint.fontpackages.oob_settings import (
            OutOfBoxFontPackageSettings,
        )

        return_type = ClientResult(context, bool())
        qry = FunctionQuery(OutOfBoxFontPackageSettings(context), "GetHideOutOfBoxFontPackages", [], return_type)
        context.add_query(qry)
        return return_type

    @staticmethod
    def set_hide_out_of_box_font_packages(context: ClientContext, hide_oob_font_packages: bool) -> ClientResult[bool]:
        """SetHideOutOfBoxFontPackages operation.

        Args:
            hide_oob_font_packages (bool):
                HideOOBFontPackages parameter
        """
        from office365.sharepoint.fontpackages.oob_settings import (
            OutOfBoxFontPackageSettings,
        )

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            OutOfBoxFontPackageSettings(context),
            "SetHideOutOfBoxFontPackages",
            None,
            {"HideOOBFontPackages": hide_oob_font_packages},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type
