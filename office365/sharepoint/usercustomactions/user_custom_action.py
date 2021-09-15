from office365.sharepoint.base_entity import BaseEntity


class UserCustomAction(BaseEntity):
    """Represents a custom action associated with a SharePoint list, Web site, or subsite."""

    @property
    def client_side_component_id(self):
        """
        :rtype: str or None
        """
        return self.properties.get("ClientSideComponentId", None)

    @property
    def script_block(self):
        """
        Gets the value that specifies the ECMAScript to be executed when the custom action is performed.
        :rtype: str or None
        """
        return self.properties.get("ScriptBlock", None)

    @script_block.setter
    def script_block(self, value):
        """
        Sets the value that specifies the ECMAScript to be executed when the custom action is performed.

        :type value: str
        """
        self.set_property("ScriptBlock", value)

    @property
    def script_src(self):
        """
        Gets a value that specifies the URI of a file which contains the ECMAScript to execute on the page
        :rtype: str or None
        """
        return self.properties.get("ScriptSrc", None)

    @script_src.setter
    def script_src(self, value):
        """
        Sets a value that specifies the URI of a file which contains the ECMAScript to execute on the page

        :type value: str
        """
        self.set_property("ScriptSrc", value)

    @property
    def url(self):
        """
        Gets or sets the URL, URI, or ECMAScript (JScript, JavaScript) function associated with the action.

        :rtype: str or None
        """
        return self.properties.get("Url", None)
