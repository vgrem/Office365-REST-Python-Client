"""Rendering of runtime objects, values and collections (``repr``/``str``)."""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from typing import Any, Optional, cast

from office365.directory.key_credential import KeyCredential
from office365.directory.users.user import User
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


def _user_collection() -> ClientObjectCollection[User]:
    return ClientObjectCollection(cast(ClientRuntimeContext, None), User, None)


def _new_user(properties: dict) -> User:
    return _user_collection().create_typed_object(properties)


@dataclass
class _Node(ClientValue):
    name: Optional[str] = None
    child: Any = None


class TestClientValueRendering(unittest.TestCase):
    def test_str_truncates_long_values(self):
        rendered = str(_Node(name="x" * 200))
        self.assertIn("…", rendered)
        self.assertLess(len(rendered), 200)

    def test_dataclass_repr_is_bounded(self):
        # ``@dataclass`` must not shadow the bounded rendering.
        rendered = repr(_Node(name="root"))
        self.assertTrue(rendered.startswith("_Node("))
        self.assertIn("name=root", rendered)
        self.assertNotIn("child", rendered)


class TestClientObjectRendering(unittest.TestCase):
    def test_domain_repr_override_is_preserved(self):
        user = _new_user({"userPrincipalName": "jane@contoso.com"})
        self.assertEqual(repr(user), "jane@contoso.com")
        self.assertEqual(str(user), repr(user))


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

    def test_html_escapes_content(self):
        collection = _user_collection()
        collection.add_child(collection.create_typed_object({"displayName": "<script>alert(1)</script>"}))
        rendered = collection._repr_html_()
        self.assertIn("<table", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<script>", rendered)

    def test_to_string_renders_all_rows(self):
        rendered = self._loaded(8).to_string()
        self.assertIn("count=8", rendered)
        self.assertIn("User 7", rendered)
        self.assertNotIn("+3 more", rendered)

    def test_to_string_max_items(self):
        rendered = self._loaded(8).to_string(max_items=2)
        self.assertIn("+6 more", rendered)
        self.assertNotIn("User 7", rendered)

    def test_to_string_does_not_truncate_identifiers(self):
        collection = _user_collection()
        long_upn = "a.very.long.guest.address#EXT#@contoso.onmicrosoft.com"
        collection.add_child(collection.create_typed_object({"displayName": "Guest", "userPrincipalName": long_upn}))

        self.assertNotIn(long_upn, repr(collection))  # the preview bounds the column
        self.assertIn(long_upn, collection.to_string())  # the report keeps it intact

    def test_repr_marks_unloaded_pages(self):
        collection = self._loaded(2)
        collection._next_request_url = "https://graph.microsoft.com/v1.0/users?$skiptoken=abc"

        rendered = repr(collection)
        self.assertIn("count=2+", rendered)  # count is a floor while pages remain
        self.assertIn("more pages available", rendered)


class TestValueCollectionRendering(unittest.TestCase):
    def test_complex_collection_renders_table(self):
        collection = ClientValueCollection(
            KeyCredential,
            [KeyCredential(displayName="A", keyId="1"), KeyCredential(displayName="B", keyId="2")],
        )
        rendered = repr(collection)
        self.assertIn("ClientValueCollection[KeyCredential](count=2)", rendered)
        self.assertIn("displayName", rendered)

    def test_to_string_renders_all_items(self):
        collection = ClientValueCollection(str, [f"item {i}" for i in range(8)])
        rendered = collection.to_string()
        self.assertIn("item 7", rendered)
        self.assertNotIn("…", rendered)


if __name__ == "__main__":
    unittest.main()
