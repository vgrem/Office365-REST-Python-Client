from __future__ import annotations

from typing import Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.folders.coloring_information import FolderColoringInformation
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


class FolderColoring(Entity):
    """"""

    def create_folder(
        self,
        decoded_url: str,
        coloring_information: FolderColoringInformation = FolderColoringInformation(),
        return_type: Optional[Folder] = None,
    ):
        """Args:
        decoded_url (str):
        coloring_information (FolderColoringInformation):
        return_type (Folder): Return type
        """
        if return_type is None:
            return_type = Folder(self.context)

        payload = {
            "path": SPResPath(decoded_url),
            "coloringInformation": coloring_information,
        }
        qry = ServiceOperationQuery(self, "CreateFolder", parameters_type=payload, return_type=return_type)
        self.context.add_query(qry)
        return return_type

    def stamp_color(self, decoded_url: str, coloring_information: FolderColoringInformation) -> Self:
        """Args:
        decoded_url (str):
        coloring_information (FolderColoringInformation):
        """
        payload = {
            "DecodedUrl": decoded_url,
            "coloringInformation": coloring_information,
        }
        qry = ServiceOperationQuery(self, "StampColor", parameters_type=payload)
        self.context.add_query(qry)
        return self

    def rename_folder(
        self, decoded_url: str, new_name: str, coloring_information: FolderColoringInformation
    ) -> ClientResult[UUID]:
        """RenameFolder operation.

        Args:
            decoded_url (str):
                DecodedUrl parameter
            new_name (str):
                newName parameter
            coloring_information (FolderColoringInformation):
                coloringInformation parameter
        """
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(
            self,
            "RenameFolder",
            None,
            {"DecodedUrl": decoded_url, "newName": new_name, "coloringInformation": coloring_information},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type
