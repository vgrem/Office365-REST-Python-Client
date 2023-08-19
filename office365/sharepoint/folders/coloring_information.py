from office365.runtime.client_value import ClientValue


class FolderColoringInformation(ClientValue):
    """"""

    def __init__(self, color_hex=None, color_tag=None, emoji=None):
        """
        :param str color_hex:
        :param str color_tag:
        :param str emoji:
        """
        self.ColorHex = color_hex
        self.ColorTag = color_tag
        self.Emoji = emoji
