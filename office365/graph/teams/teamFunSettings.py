from office365.runtime.clientValue import ClientValue


class TeamFunSettings(ClientValue):
    """Settings to configure use of Giphy, memes, and stickers in the team."""

    def __init__(self):
        super().__init__()
        self.allowGiphy = True
