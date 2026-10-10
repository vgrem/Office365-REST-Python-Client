from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.v3.static import StaticPath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata
from office365.sharepoint.entity import Entity
from office365.sharepoint.social.thread import SocialThread

if TYPE_CHECKING:
    from office365.sharepoint.social.actor import SocialActor


class SocialRestThread(Entity):
    """
    The SocialRestThread class specifies a thread that is stored on the server. The thread contains a root post
    and zero or more reply posts. The SocialRestThread type is available when the protocol client sends an OData
    request to a protocol server using [MS-CSOMREST]. It is not available using [MS-CSOM].
    """

    @property
    def resource_path(self):
        if self._resource_path is None:
            self._resource_path = StaticPath("SP.Social.SocialRestThread")
        return self._resource_path

    def like(self, post_id: str) -> Self:
        """The Like method makes the current user a liker of the specified post.

        Args:
            post_id (str): Specifies the post by its identifier.
        """
        payload = {"ID": post_id}
        qry = ServiceOperationQuery(self, "Like", None, payload, None, self)
        self.context.add_query(qry)
        return self

    def unlike(self, post_id: str) -> Self:
        """The Unlike method removes the current user from the list of likers for the specified post.
        If the current is not a liker of the post, this method has no effect.

        Args:
            post_id (str): Specifies the post by its identifier.
        """
        payload = {"ID": post_id}
        qry = ServiceOperationQuery(self, "UnLike", None, payload, None, self)
        self.context.add_query(qry)
        return self

    @odata(name="SocialThread")
    @property
    def social_thread(self) -> SocialThread:
        """The SocialThread property provides the object that contains the thread"""
        return self.properties.get("SocialThread", SocialThread())

    @property
    def id_(self) -> Optional[str]:
        """Gets the ID property"""
        return self.properties.get("ID", None)

    @property
    def entity_type_name(self):
        return "SP.Social.SocialRestThread"

    @property
    def id(self) -> Optional[str]:
        """Gets the ID property"""
        return self.properties.get("ID", None)

    def delete(self, id_: str) -> Self:
        """Delete operation.

        Args:
            id_ (str):
                ID parameter
        """
        qry = ServiceOperationQuery(self, "Delete", None, {"ID": id_}, None, None)
        self.context.add_query(qry)
        return self

    def likers(self, id_: str) -> ClientResult[ClientValueCollection[SocialActor]]:
        """Likers operation.

        Args:
            id_ (str):
                ID parameter
        """
        from office365.sharepoint.social.actor import SocialActor

        return_type = ClientResult(self.context, ClientValueCollection[SocialActor]())
        qry = FunctionQuery(self, "Likers", [id_], return_type)
        self.context.add_query(qry)
        return return_type
