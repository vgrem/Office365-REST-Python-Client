from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


class MoveCopyUtil(BaseEntity):
    """A container class for static move/copy methods."""

    @staticmethod
    def copy_file_by_path(context, src_path, dest_path, overwrite, options=None):
        """
        Copies a file from a source URL to a destination URL.

        :param office365.sharepoint.client_context.ClientContext context: client context
        :param str src_path: A full or server relative path that represents the source file.
        :param str dest_path:  A full or server relative url that represents the destination file.
        :param bool overwrite: Overwrites the destination file when it exists.
        :param office365.sharepoint.utilities.move_copy_options.MoveCopyOptions or None options:
        """
        return_type = ClientResult(context)
        payload = {
            "srcPath": SPResPath.create_absolute(context.base_url, src_path),
            "destPath": SPResPath.create_absolute(context.base_url, dest_path),
            "overwrite": overwrite,
            "options": options
        }
        qry = ServiceOperationQuery(MoveCopyUtil(context), "CopyFileByPath", None, payload, None, return_type, True)
        context.add_query(qry)
        return return_type

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
        return_type = ClientResult(context)
        binding_type = MoveCopyUtil(context)
        payload = {
            "srcUrl": str(SPResPath.create_absolute(context.base_url, src_url)),
            "destUrl": str(SPResPath.create_absolute(context.base_url, dest_url)),
            "options": options
        }
        qry = ServiceOperationQuery(binding_type, "CopyFolder", None, payload, None, return_type, True)
        context.add_query(qry)
        return return_type

    @staticmethod
    def copy_folder_by_path(context, src_path, dest_path, options=None):
        """
        Copies a folder from a source URL to a destination URL.

        :param office365.sharepoint.client_context.ClientContext context: client context
        :param str src_path: A full or server relative path that represents the source folder.
        :param str dest_path:  A full or server relative url that represents the destination folder.
        :param office365.sharepoint.utilities.move_copy_options.MoveCopyOptions or None options:
        """
        return_type = ClientResult(context)
        payload = {
            "srcPath": SPResPath.create_absolute(context.base_url, src_path),
            "destPath": SPResPath.create_absolute(context.base_url, dest_path),
            "options": options
        }
        qry = ServiceOperationQuery(MoveCopyUtil(context), "CopyFolderByPath", None, payload, None, return_type, True)
        context.add_query(qry)
        return return_type

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
        binding_type = MoveCopyUtil(context)
        payload = {
            "srcUrl": str(SPResPath.create_absolute(context.base_url, src_url)),
            "destUrl": str(SPResPath.create_absolute(context.base_url, dest_url)),
            "options": options
        }
        qry = ServiceOperationQuery(binding_type, "MoveFolder", None, payload, None, None, True)
        context.add_query(qry)
        return binding_type

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
        binding_type = MoveCopyUtil(context)
        payload = {
            "srcPath": SPResPath.create_absolute(context.base_url, src_path),
            "destPath": SPResPath.create_absolute(context.base_url, dest_path),
            "options": options
        }
        qry = ServiceOperationQuery(binding_type, "MoveFolderByPath", None, payload, None, None, True)
        context.add_query(qry)
        return binding_type
