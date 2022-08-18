from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.folders.folder import Folder


class DocumentSet(Folder):

    @staticmethod
    def create(context, parent_folder, name, ct_id="0x0120D520"):
        """Creates a new DocumentSet object.

        :type context: office365.sharepoint.client_context.ClientContext
        :type parent_folder: office365.sharepoint.folders.folder.Folder
        :type name: str
        :type ct_id: office365.sharepoint.contenttypes.content_type_id.ContentTypeId
        """

        return_type = DocumentSet(context)

        def _get_list_details():
            custom_props = parent_folder.get_property("Properties")
            list_id = custom_props.get('vti_x005f_listname')
            target_list = context.web.lists.get_by_id(list_id)
            target_list.ensure_property("Title", _create_doc_set, target_list=target_list)

        def _create_doc_set(target_list):
            list_name = target_list.title.replace(" ", "")
            request_url = r"{0}/_vti_bin/listdata.svc/{1}".format(context.base_url, list_name)
            request = RequestOptions(request_url)
            request.method = HttpMethod.Post
            folder_url = parent_folder.serverRelativeUrl + '/' + name
            return_type._resource_path = ServiceOperationPath("getFolderByServerRelativeUrl", [folder_url],
                                                              ResourcePath("Web"))
            request.set_header('Slug', '{0}|{1}'.format(folder_url, ct_id))
            response = context.pending_request().execute_request_direct(request)
            response.raise_for_status()
            json = response.json()
            context.pending_request().map_json(json, return_type)

        parent_folder.ensure_properties(["Properties", "ServerRelativeUrl"], _get_list_details)
        return return_type

    def set_property(self, name, value, persist_changes=True):
        super(Folder, self).set_property(name, value, persist_changes)
        return self
