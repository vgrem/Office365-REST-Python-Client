from office365.runtime.client_value import ClientValue


class TitleArea(ClientValue):
    """Represents the title area of a given SharePoint page."""

    def __init__(self, alternativeText=None, enableGradientEffect=None):
        """
        :param str alternativeText: Alternative text on the title area.
        :param bool enableGradientEffect: Indicates whether the title area has a gradient effect enabled.
        """
        self.alternativeText = alternativeText
        self.enableGradientEffect = enableGradientEffect
