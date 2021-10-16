from office365.onedrive.internal.queries.upload_session_query import UploadSessionQuery
from office365.outlook.mail.attachments.attachment_item import AttachmentItem
from office365.outlook.mail.attachments.attachment_type import AttachmentType
from office365.runtime.compat import parse_query_string
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.client_query import ClientQuery


class AttachmentUploadQuery(UploadSessionQuery):
    """Create an upload session to allow your app to upload attachments up to the maximum file size. An upload session
    allows your app to upload ranges of the file in sequential API requests, which allows the transfer to be resumed
    if a connection is dropped while the upload is in progress. """

    def __init__(self, session_item, source_path, chunk_size=1024, chunk_uploaded=None):
        super(AttachmentUploadQuery, self).__init__(session_item, source_path,
                                                    chunk_size=chunk_size,
                                                    chunk_uploaded=chunk_uploaded)

    def create_upload_session(self):
        attachment_item = AttachmentItem(attachment_type=AttachmentType.file, name=self.file_name, size=self.file_size)
        return self.binding_type.create_upload_session(attachment_item)

    def _create_next_range_query(self, resp):
        super(AttachmentUploadQuery, self)._create_next_range_query(resp)
        location = resp.headers.get("Location", None)
        if location is not None:
            qry = ClientQuery(self.context, self.binding_type)

            def _construct_get_attachment_request(request):
                """
                :type request: office365.runtime.http.request_options.RequestOptions
                """
                request.url = location.replace("https://outlook.office.com/api/gv1.0", self.context.service_root_url())
                request.method = HttpMethod.Get

            self.context.before_execute(_construct_get_attachment_request)
            self.context.add_query(qry, True)

    def _construct_range_request(self, request):
        super(AttachmentUploadQuery, self)._construct_range_request(request)
        auth_token = parse_query_string(request.url, "authtoken")
        request.set_header('Authorization', 'Bearer {0}'.format(auth_token))
