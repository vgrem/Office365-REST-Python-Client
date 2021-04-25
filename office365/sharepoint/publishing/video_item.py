from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class VideoItem(BaseEntity):

    def get_video_embed_code(self, width, height, autoplay=True, showInfo=True, makeResponsive=True):
        """

        :type width: int
        :type height: int
        :type autoplay: bool
        :type showInfo: bool
        :type makeResponsive: bool
        """
        return_type = ClientResult(self.context)
        params = {"width": width, "height": height, "autoplay": autoplay,
                  "showInfo": showInfo, "makeResponsive": makeResponsive}
        qry = ServiceOperationQuery(self, "GetVideoEmbedCode", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type
