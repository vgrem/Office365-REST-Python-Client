from office365.runtime.client_value import ClientValue


class ThemeData(ClientValue):
    """ """

    def __init__(self, name=None, source=None, is_themes_v2=None, theme_json=None):
        self.name = name
        self.source = source
        self.isThemesV2 = is_themes_v2
        self.themeJson = theme_json
