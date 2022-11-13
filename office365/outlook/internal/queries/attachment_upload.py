from office365.runtime.compat import parse_query_string
from office365.runtime.odata.v4.upload_session_request import UploadSessionRequest
from office365.outlook.mail.attachments.attachment_item import AttachmentItem
from office365.runtime.queries.upload_session import UploadSessionQuery


def create_attachment_upload_query(binding_type, return_type, source_path, chunk_size=1000000, chunk_uploaded=None):
    """
    :type binding_type: office365.outlook.mail.attachments.collection.AttachmentCollection
    :type return_type: FileAttachment
    :type source_path: str
    :type chunk_size: int
    :type chunk_uploaded: (int)->None
    """
    qry = UploadSessionQuery(binding_type, {"AttachmentItem": AttachmentItem.create_file(source_path)})
    context = binding_type.context

    def _start_upload(resp):
        """
        :type resp: requests.Response
        """
        resp.raise_for_status()
        with open(source_path, 'rb') as local_file:
            session_request = UploadSessionRequest(local_file, chunk_size, chunk_uploaded)

            def _construct_request(request):
                auth_token = parse_query_string(request.url, "authtoken")
                request.set_header('Authorization', 'Bearer {0}'.format(auth_token))
            session_request.beforeExecute += _construct_request

            def _process_response(response):
                """
                :type response: requests.Response
                """
                location = response.headers.get("Location", None)
                if location is None:
                    return
                attachment_id = location[location.find("Attachments(") + 13:-2]
                return_type.set_property("id", attachment_id)
            session_request.afterExecute += _process_response

            session_request.execute_query(qry)

    context.after_execute(_start_upload)
    return qry
