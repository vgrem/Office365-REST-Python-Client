from functools import lru_cache, wraps
from typing import Any, Callable, TypeVar
from unittest import TestCase

from office365.directory.applications.roles.collection import AppRoleCollection
from office365.graph_client import GraphClient
from office365.runtime.types.collections import StringCollection
from tests import test_client_id

T = TypeVar("T", bound=Callable[..., Any])


@lru_cache(maxsize=1)
def _get_cached_permissions(client, client_id):
    # type: (GraphClient, str) -> AppRoleCollection
    """Get and cache application permissions for a client"""
    resource = client.service_principals.get_by_name("Microsoft Graph")
    result = resource.get_application_permissions(client_id).execute_query()
    return result.value


def requires_app_permission(app_role):
    # type: (str) -> Callable[[T], T]
    def decorator(test_method):
        # type: (T) -> T
        @wraps(test_method)
        def wrapper(self, *args, **kwargs):
            # type: (TestCase, *Any, **Any) -> Any
            client = getattr(self, "client", None)
            if not client:
                self.skipTest("No client available for permission check")

            try:
                permissions = _get_cached_permissions(client, test_client_id)

                if not any(role.value == app_role for role in permissions):
                    self.skipTest(f"Required app permission '{app_role}' not granted")

                return test_method(self, *args, **kwargs)

            except Exception as e:
                self.skipTest(f"Permission check failed: {str(e)}")

        return wrapper

    return decorator


@lru_cache(maxsize=1)
def _get_cached_delegated_permissions(client, client_id):
    # type: (GraphClient, str) -> StringCollection
    """Get and cache delegated permissions for a client"""
    resource = client.service_principals.get_by_name("Microsoft Graph")
    result = resource.get_delegated_permissions(client_id).execute_query()
    return result.value


def requires_delegated_permission(*scopes):
    # type: (*str) -> Callable[[T], T]
    """Decorator to verify delegated permissions before test execution"""

    def decorator(test_method):
        # type: (T) -> T
        @wraps(test_method)
        def wrapper(self, *args, **kwargs):
            # type: (TestCase, *Any, **Any) -> Any
            client = getattr(self, "client", None)
            if not client:
                self.skipTest("No client available for permission check")

            try:
                # Get permissions from cache or API
                granted_scopes = _get_cached_delegated_permissions(client, test_client_id)

                if not any(scope in granted_scopes for scope in scopes):
                    self.skipTest(
                        f"Required delegated permission '{', '.join(scopes)}' not granted"
                    )

                return test_method(self, *args, **kwargs)

            except Exception as e:
                self.skipTest(f"Permission check failed: {str(e)}")

        return wrapper  # type: ignore[return-value]

    return decorator
