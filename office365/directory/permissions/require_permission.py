from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, TypeVar, cast

from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class PermissionRequirement:
    """Declares the permissions required to call an API method.

    Fields map directly to the official Microsoft Graph docs tables
    (Delegated / Application columns, plus optional Entra ID roles).

    Stamped as ``method.__required_permissions__`` by :func:`require_permission`
    and attached to the query the method queues, so a denied request can name
    the missing permission via :meth:`to_hint`.
    """

    delegated: list[str] = field(default_factory=list)
    application: list[str] = field(default_factory=list)
    directory_roles: list[str] = field(default_factory=list)
    licenses: list[str] = field(default_factory=list)
    notes: str = ""

    def to_hint(self) -> str:
        """One-line remediation naming the declared permissions (may be empty).

        Shown by an :class:`~office365.runtime.exceptions.AccessDeniedException`
        when a decorated method's request is rejected.
        """
        scopes: list[str] = []
        if self.application:
            scopes.append(f"application {', '.join(self.application)}")
        if self.delegated:
            scopes.append(f"delegated {', '.join(self.delegated)}")
        if self.directory_roles:
            scopes.append(f"directory role {', '.join(self.directory_roles)}")
        if not scopes:
            return ""
        hint = "This API declares: " + "; ".join(scopes) + "."
        if self.notes:
            hint += f" ({self.notes})"
        return hint


def require_permission(
    delegated: list[str] | None = None,
    application: list[str] | None = None,
    directory_roles: list[str] | None = None,
    licenses: list[str] | None = None,
    notes: str = "",
):
    """Annotate a method with the permissions it requires.

    The declaration enriches the docstring (so ``help(method)`` shows the
    required permissions) and is stamped as ``method.__required_permissions__``.
    The decorated method also tags the query it builds, so if the request is
    denied (HTTP 401/403) the raised
    :class:`~office365.runtime.exceptions.AccessDeniedException` names the
    declared permission. The only runtime cost is a local attribute read/write
    per call — no network calls, no authentication, no type checking.

    The ``delegated`` and ``application`` parameters map directly to the
    columns in the official Microsoft Graph REST API documentation.

    View the declared permissions with :func:`help`::

        from office365.onedrive.drives.collection import DriveCollection

        help(DriveCollection.get)
    """
    req = PermissionRequirement(
        delegated=delegated or [],
        application=application or [],
        directory_roles=directory_roles or [],
        licenses=licenses or [],
        notes=notes,
    )

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        def context_of(owner: Any) -> Any:
            context: Any = getattr(owner, "context", None)
            return context if hasattr(context, "last_query") else None

        def previous_query(owner: Any) -> Any:
            context: Any = context_of(owner)
            return None if context is None else context.last_query

        def stamp(owner: Any, previous: Any) -> None:
            # Tag the query this builder queued with the declaration, so a later
            # denial can name the permission. A method that queues nothing leaves
            # the previous query untouched.
            context: Any = context_of(owner)
            if context is None:
                return
            query = context.last_query
            if query is not None and query is not previous:
                query.permission_requirement = req

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            owner = args[0] if args else None
            previous = previous_query(owner)
            result: Any = func(*args, **kwargs)
            if inspect.iscoroutine(result):

                async def run_and_stamp() -> Any:
                    try:
                        return await result
                    finally:
                        stamp(owner, previous)

                return run_and_stamp()
            stamp(owner, previous)
            return result

        wrapper.__dict__["__required_permissions__"] = req

        lines: list[str] = []
        if req.delegated:
            lines.append(f"      Delegated: {', '.join(req.delegated)}")
        if req.application:
            lines.append(f"      Application: {', '.join(req.application)}")
        if req.directory_roles:
            lines.append(f"      Directory roles: {', '.join(req.directory_roles)}")
        if req.licenses:
            lines.append(f"      Licenses: {', '.join(req.licenses)}")
        if req.notes:
            lines.append(f"      Notes: {req.notes}")

        if lines:
            extra = "\n    Requires permissions:\n" + "\n".join(lines)
            wrapper.__doc__ = (wrapper.__doc__ or "") + extra

        return cast("Callable[P, R]", wrapper)

    return decorator
