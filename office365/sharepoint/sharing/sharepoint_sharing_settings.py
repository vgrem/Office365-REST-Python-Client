from __future__ import annotations

from typing import Optional

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata
from office365.sharepoint.entity import Entity
from office365.sharepoint.sharing.picker_settings import PickerSettings


class SharePointSharingSettings(Entity):
    """This class contains the SharePoint UI-specific sharing settings."""

    @odata(name="PickerProperties")
    @property
    def picker_properties(self) -> PickerSettings:
        """An object containing the necessary information to initialize a client people picker control used
        to search for and resolve desired users and groups."""
        return self.properties.get(
            "PickerProperties",
            PickerSettings(self.context, ResourcePath("PickerProperties", self.resource_path)),
        )

    @property
    def add_to_group_mode_name(self) -> Optional[str]:
        """Gets the AddToGroupModeName property"""
        return self.properties.get("AddToGroupModeName", None)

    @property
    def group_name_lines(self) -> StringCollection:
        """Gets the GroupNameLines property"""
        return self.properties.get("GroupNameLines", StringCollection())

    @property
    def group_role_definition_names_lines(self) -> StringCollection:
        """Gets the GroupRoleDefinitionNamesLines property"""
        return self.properties.get("GroupRoleDefinitionNamesLines", StringCollection())

    @property
    def is_mobile_view(self) -> Optional[bool]:
        """Gets the IsMobileView property"""
        return self.properties.get("IsMobileView", None)

    @property
    def panel_give_permissions_visible(self) -> Optional[bool]:
        """Gets the PanelGivePermissionsVisible property"""
        return self.properties.get("PanelGivePermissionsVisible", None)

    @property
    def panel_show_hide_more_options_visible(self) -> Optional[bool]:
        """Gets the PanelShowHideMoreOptionsVisible property"""
        return self.properties.get("PanelShowHideMoreOptionsVisible", None)

    @property
    def panel_simplified_role_selector_visible(self) -> Optional[bool]:
        """Gets the PanelSimplifiedRoleSelectorVisible property"""
        return self.properties.get("PanelSimplifiedRoleSelectorVisible", None)

    @property
    def required_script_file_links(self) -> StringCollection:
        """Gets the RequiredScriptFileLinks property"""
        return self.properties.get("RequiredScriptFileLinks", StringCollection())

    @property
    def role_definition_name_lines(self) -> StringCollection:
        """Gets the RoleDefinitionNameLines property"""
        return self.properties.get("RoleDefinitionNameLines", StringCollection())

    @property
    def selected_group(self) -> Optional[str]:
        """Gets the SelectedGroup property"""
        return self.properties.get("SelectedGroup", None)

    @property
    def shared_with_enabled(self) -> Optional[bool]:
        """Gets the SharedWithEnabled property"""
        return self.properties.get("SharedWithEnabled", None)

    @property
    def sharing_css_link(self) -> Optional[str]:
        """Gets the SharingCssLink property"""
        return self.properties.get("SharingCssLink", None)

    @property
    def tabbed_dialog_enabled(self) -> Optional[bool]:
        """Gets the TabbedDialogEnabled property"""
        return self.properties.get("TabbedDialogEnabled", None)

    @property
    def tab_to_show(self) -> Optional[int]:
        """Gets the TabToShow property"""
        return self.properties.get("TabToShow", None)

    @property
    def txt_email_subject_text(self) -> Optional[str]:
        """Gets the txtEmailSubjectText property"""
        return self.properties.get("txtEmailSubjectText", None)

    @property
    def user_display_url(self) -> Optional[str]:
        """Gets the UserDisplayUrl property"""
        return self.properties.get("UserDisplayUrl", None)
