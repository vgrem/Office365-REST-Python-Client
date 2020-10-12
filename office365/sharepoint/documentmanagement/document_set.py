from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.base_entity import BaseEntity


class DocumentSet(BaseEntity):

    @staticmethod
    def create(context, parentFolder, name, ctid="0x0120D520"):
        """Creates a new DocumentSet object.

        :type context: office365.sharepoint.client_context.ClientContext
        :type parentFolder: office365.sharepoint.folders.folder.Folder
        :type name: str
        :type ctid: office365.sharepoint.contenttypes.content_type_id.ContentTypeId
        """
        result = DocumentSet(context)

        def _create_doc_set():

            url = r"{0}/_vti_bin/listdata.svc/{1}".format(context.base_url,
                                                          parentFolder.properties["Name"].replace(" ", ""))
            request = RequestOptions(url)
            request.method = HttpMethod.Post
            folder_url = parentFolder.serverRelativeUrl + '/' + name
            request.set_header('Slug', '{0}|{1}'.format(folder_url, ctid))
            response = context.execute_request_direct(request)
            json = response.json()
            context.pending_request().map_json(json, result)

        parentFolder.ensure_properties(["ServerRelativeUrl", "Name"], _create_doc_set)
        return result
