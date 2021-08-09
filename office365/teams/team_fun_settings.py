from office365.runtime.client_value import ClientValue


class TeamFunSettings(ClientValue):
    """Settings to configure use of Giphy, memes, and stickers in the team."""

    def __init__(self):
        super(TeamFunSettings, self).__init__()
        self.allowGiphy = True
