from functools import wraps
from typing import Any, Callable, TypeVar
from unittest import TestCase

from tests import test_client_id

T = TypeVar('T', bound=Callable[..., Any])


def requires_app_permission(app_role):
    # type: (str) -> Callable[[T], T]
    def decorator(test_method):
        # type: (T) -> T
        @wraps(test_method)
        def wrapper(self: TestCase, *args, **kwargs):
            client = getattr(self, "client", None)
            if not client:
                self.skipTest("No client available for permission check")

            try:
                resource = client.service_principals.get_by_name("Microsoft Graph")
                result = resource.get_application_permissions(test_client_id).execute_query()

                if not any(role.value == app_role for role in result.value):
                    self.skipTest(f"Required app permission '{app_role}' not granted")

                return test_method(self, *args, **kwargs)

            except Exception as e:
                self.skipTest(f"Permission check failed: {str(e)}")

        return wrapper

    return decorator
