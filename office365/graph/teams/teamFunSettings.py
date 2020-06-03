from office365.runtime.client_value_object import ClientValueObject


class TeamFunSettings(ClientValueObject):
    """Settings to configure use of Giphy, memes, and stickers in the team."""

    def __init__(self):
        super().__init__()
        self.allowGiphy = True

