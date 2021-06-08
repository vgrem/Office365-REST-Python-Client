from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class MoveCopyUtil(BaseEntity):

    @staticmethod
    def copy_folder(context, srcUrl, destUrl, options):
        """

        :param office365.sharepoint.utilities.move_copy_options.MoveCopyOptions options:
        :param str srcUrl:
        :param str destUrl:
        :param office365.sharepoint.client_context.ClientContext context: client context
        """
        result = ClientResult(context)
        util = MoveCopyUtil(context)
        payload = {
            "srcUrl": srcUrl,
            "destUrl": destUrl,
            "options": options
        }
        qry = ServiceOperationQuery(util, "CopyFolder", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def move_folder(context, srcUrl, destUrl, options):
        """

        :param office365.sharepoint.utilities.move_copy_options.MoveCopyOptions options:
        :param str srcUrl:
        :param str destUrl:
        :param office365.sharepoint.client_context.ClientContext context: client context
        """
        util = MoveCopyUtil(context)
        payload = {
            "srcUrl": srcUrl,
            "destUrl": destUrl,
            "options": options
        }
        qry = ServiceOperationQuery(util, "MoveFolder", None, payload, None, None)
        qry.static = True
        context.add_query(qry)
        return util
