from office365.runtime.client_value import ClientValue


class BrandCenterConfiguration(ClientValue):
    """ """

    def __init__(self, brand_colors_list_id=None, brand_colors_list_url=None):
        self.BrandColorsListId = brand_colors_list_id
        self.BrandColorsListUrl = brand_colors_list_url
