from office365.runtime.paths.service_operation import ServiceOperationPath


class AttachmentPath(ServiceOperationPath):
    """Path for addressing an attachment file"""

    def __init__(self, file_name, parent=None):
        super().__init__("GetByFileName", [file_name], parent)
