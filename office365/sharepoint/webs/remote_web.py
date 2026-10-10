from __future__ import annotations

from typing import Optional

from office365.onedrive.lists.list import List
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.webs.web import Web


class RemoteWeb(Entity):
    """Specifies a remote web that might be on a different domain."""

    def get_list_by_server_relative_url(self, server_relative_url):
        """Returns the list that is associated with the specified server-relative URL.

        Args:
            server_relative_url (str): A string that contains the site-relative URL for a list.
        """
        target_list = List(self.context)
        qry = ServiceOperationQuery(
            self,
            "GetListByServerRelativeUrl",
            [server_relative_url],
            None,
            None,
            target_list,
        )
        self.context.add_query(qry)
        return target_list

    @staticmethod
    def create(context, request_url: str) -> "RemoteWeb":
        """Args:
        context (ClientContext):
        request_url (str):
        """
        remote_web = RemoteWeb(context)
        qry = ServiceOperationQuery(context, None, [request_url], None, None, remote_web)
        qry.static = True
        context.add_query(qry)
        return remote_web

    @property
    def web(self):
        """Gets the SPWeb."""
        return self.properties.get("Web", Web(self.context, ResourcePath("Web", self.resource_path)))

    @property
    def can_send_email(self) -> Optional[bool]:
        """Gets the CanSendEmail property"""
        return self.properties.get("CanSendEmail", None)

    @property
    def share_by_email_enabled(self) -> Optional[bool]:
        """Gets the ShareByEmailEnabled property"""
        return self.properties.get("ShareByEmailEnabled", None)

    @property
    def share_by_link_enabled(self) -> Optional[bool]:
        """Gets the ShareByLinkEnabled property"""
        return self.properties.get("ShareByLinkEnabled", None)
