from office365.runtime.client_value_object import ClientValueObject


class File(ClientValueObject):

    def __init__(self):
        super(File, self).__init__()
        self.hashes = None
        self.mimeType = None
        self.processingMetadata = None
