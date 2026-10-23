"""Rendering of runtime objects, values and collections (``repr``/``str``)."""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from typing import Any, Optional, cast

from office365.directory.users.user import User
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.client_value import ClientValue


def _user_collection() -> ClientObjectCollection[User]:
    return ClientObjectCollection(cast(ClientRuntimeContext, None), User, None)


@dataclass
class _Node(ClientValue):
    name: Optional[str] = None
    child: Any = None


class TestClientValueRendering(unittest.TestCase):
    def test_dataclass_repr_is_bounded(self):
        # ``@dataclass`` must not shadow the bounded rendering.
        rendered = repr(_Node(name="root"))
        self.assertTrue(rendered.startswith("_Node("))
        self.assertIn("name=root", rendered)
        self.assertNotIn("child", rendered)


class TestObjectCollectionRendering(unittest.TestCase):
    def _loaded(self, count: int) -> ClientObjectCollection[User]:
        collection = _user_collection()
        for index in range(count):
            collection.add_child(
                collection.create_typed_object(
                    {"displayName": f"User {index}", "userPrincipalName": f"user{index}@contoso.com"}
                )
            )
        return collection

    def test_to_string_does_not_truncate_identifiers(self):
        collection = _user_collection()
        long_upn = "a.very.long.guest.address#EXT#@contoso.onmicrosoft.com"
        collection.add_child(collection.create_typed_object({"displayName": "Guest", "userPrincipalName": long_upn}))

        self.assertNotIn(long_upn, repr(collection))  # the preview bounds the column
        self.assertIn(long_upn, collection.to_string())  # the report keeps it intact


if __name__ == "__main__":
    unittest.main()
