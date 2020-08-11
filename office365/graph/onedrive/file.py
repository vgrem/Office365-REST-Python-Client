from office365.runtime.client_value import ClientValue


class File(ClientValue):

    def __init__(self):
        super(File, self).__init__()
        self.hashes = None
        self.mimeType = None
        self.processingMetadata = None
