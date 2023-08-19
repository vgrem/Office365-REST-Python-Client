from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.folders.folder import Folder


class FolderColoring(BaseEntity):
    """"""

    def create_folder(self, decoded_url, ensure_unique_file_name=True, overwrite=True, coloring_information=None):
        """
        :param str decoded_url:
        :param bool ensure_unique_file_name:
        :param bool overwrite:
        :param FolderColoringInformation coloring_information:
        """
        return_type = Folder(self.context)

        payload = {
            "DecodedUrl": decoded_url,
            "EnsureUniqueFileName": ensure_unique_file_name,
            "Overwrite": overwrite,
            "coloringInformation": coloring_information
        }
        qry = ServiceOperationQuery(self, "CreateFolder", parameters_type=payload, return_type=return_type)
        self.context.add_query(qry)
        return return_type

    def stamp_color(self, decoded_url, coloring_information):
        """
        :param str decoded_url:
        :param FolderColoringInformation coloring_information:
        """
        payload = {
            "DecodedUrl": decoded_url,
            "coloringInformation": coloring_information
        }
        qry = ServiceOperationQuery(self, "StampColor", parameters_type=payload)
        self.context.add_query(qry)
        return self
