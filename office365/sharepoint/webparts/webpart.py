from office365.sharepoint.base_entity import BaseEntity


class WebPart(BaseEntity):
    """
    A reusable component that contains or generates web-based content such as XML, HTML, and scripting code.
    It has a standard property schema and displays that content in a cohesive unit on a webpage. See also Web Parts Page
    """

    @property
    def zone_index(self):
        """
        An integer that specifies the relative position of a Web Part in a Web Part zone.
        Web Parts are positioned from the smallest to the largest zone index. If two or more Web Parts have the
        same zone index they are positioned adjacent to each other in an undefined order
        :rtype: int or None
        """
        return self.properties.get("ZoneIndex", None)

    @property
    def entity_type_name(self):
        return "SP.WebParts.WebPart"
