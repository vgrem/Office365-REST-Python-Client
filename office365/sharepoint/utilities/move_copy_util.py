from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


class MoveCopyUtil(BaseEntity):
    """A container class for static move/copy methods."""

    @staticmethod
    def copy_folder(context, src_url, dest_url, options=None):
        """
        Copies a folder from a source URL to a destination URL.

        :param office365.sharepoint.client_context.ClientContext context: Client context
        :param str src_url: A full or server relative url that represents the source folder.
        :param str dest_url: A full or server relative url that represents the destination folder.
        :param office365.sharepoint.utilities.move_copy_options.MoveCopyOptions options: Contains options used to
            modify the behavior.
        """
        result = ClientResult(context)
        util = MoveCopyUtil(context)
        payload = {
            "srcUrl": context.create_safe_url(src_url, False),
            "destUrl": context.create_safe_url(dest_url, False),
            "options": options
        }
        qry = ServiceOperationQuery(util, "CopyFolder", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def copy_folder_by_path(context, src_path, dest_path, options=None):
        """
        Copies a folder from a source URL to a destination URL.

        :param office365.sharepoint.client_context.ClientContext context: client context
        :param str src_path: A full or server relative path that represents the source folder.
        :param str dest_path:  A full or server relative url that represents the destination folder.
        :param office365.sharepoint.utilities.move_copy_options.MoveCopyOptions or None options:
        """
        result = ClientResult(context)
        util = MoveCopyUtil(context)
        payload = {
            "srcPath": SPResPath(context.create_safe_url(src_path, False)),
            "destPath": SPResPath(context.create_safe_url(dest_path, False)),
            "options": options
        }
        qry = ServiceOperationQuery(util, "CopyFolderByPath", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def move_folder(context, src_url, dest_url, options):
        """
        Moves a folder from a source URL to a destination URL.

        :param office365.sharepoint.client_context.ClientContext context: client context
        :param str src_url: A full or server relative url that represents the source folder.
        :param str dest_url: A full or server relative url that represents the destination folder.
        :param office365.sharepoint.utilities.move_copy_options.MoveCopyOptions options: Contains options used to
            modify the behavior.
        """
        util = MoveCopyUtil(context)
        payload = {
            "srcUrl": context.create_safe_url(src_url, False),
            "destUrl": context.create_safe_url(dest_url, False),
            "options": options
        }
        qry = ServiceOperationQuery(util, "MoveFolder", None, payload)
        qry.static = True
        context.add_query(qry)
        return util

    @staticmethod
    def move_folder_by_path(context, src_path, dest_path, options):
        """
        Moves a folder from a source URL to a destination URL.

        :param str src_path: A full or server relative path that represents the source folder.
        :param str dest_path: A full or server relative path that represents the destination folder.
        :param office365.sharepoint.client_context.ClientContext context: client context
        :param office365.sharepoint.utilities.move_copy_options.MoveCopyOptions options: Contains options used
            to modify the behavior.
        """
        util = MoveCopyUtil(context)
        payload = {
            "srcPath": SPResPath(context.create_safe_url(src_path, False)),
            "destPath": SPResPath(context.create_safe_url(dest_path, False)),
            "options": options
        }
        qry = ServiceOperationQuery(util, "MoveFolderByPath", None, payload)
        qry.static = True
        context.add_query(qry)
        return util
