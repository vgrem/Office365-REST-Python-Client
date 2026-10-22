from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Union

from typing_extensions import Self

from office365.runtime.client_value import ClientValue
from office365.sharepoint.permissions.kind import PermissionKind


@dataclass
class BasePermissions(ClientValue):
    """Specifies a set of built-in permissions."""

    _BITS_PER_INT = 32
    _MAX_BITS = 64
    _FULL_MASK = 0xFFFF

    High: int = 0
    Low: int = 0

    def __repr__(self):
        perms = self.permission_levels
        return f"BasePermissions({', '.join(perms)})" if perms else "BasePermissions(Empty)"

    def __iter__(self) -> Iterator[str]:  # type: ignore[override]
        for perm in PermissionKind:
            if perm != PermissionKind.EmptyMask and self.has(perm):
                yield perm.name

    def __contains__(self, perm: Union[PermissionKind, int]) -> bool:
        return self.has(perm)

    def set(self, perm: Union[PermissionKind, int]) -> None:
        """Sets a permission with support for both enum and raw integer values."""
        if isinstance(perm, int):
            perm = PermissionKind(perm)
        if perm == PermissionKind.FullMask:
            self.Low = self.High = self._FULL_MASK
        elif perm == PermissionKind.EmptyMask:
            self.Low = self.High = 0
        else:
            bit_pos = perm.value - 1
            mask = 1 << (bit_pos % self._BITS_PER_INT)
            if bit_pos < self._BITS_PER_INT:
                self.Low |= mask
            elif self._BITS_PER_INT <= bit_pos < self._MAX_BITS:
                self.High |= mask

    def has(self, perm: Union[PermissionKind, int]) -> bool:
        """Checks if permission is set with support for both enum and integer values."""
        if isinstance(perm, int):
            perm = PermissionKind(perm)
        if perm == PermissionKind.EmptyMask:
            return True
        if perm == PermissionKind.FullMask:
            return self.Low == self._FULL_MASK and self.High == self._FULL_MASK
        bit_pos = perm.value - 1
        if not 0 <= bit_pos < self._MAX_BITS:
            return False
        mask = 1 << (bit_pos % self._BITS_PER_INT)
        return bool(self.Low & mask) if bit_pos < self._BITS_PER_INT else bool(self.High & mask)

    def clear_all(self):
        """Clears all permissions for the current instance."""
        self.High = 0
        self.Low = 0

    def to_json(self, profile=None):
        return {"Low": str(self.Low), "High": str(self.High)}

    def set_property(self, k: str | int, v: Any, persist_changes: bool = True) -> Self:
        if k in ("Low", "High"):
            setattr(self, k, int(v))
        return self

    @property
    def permission_levels(self):
        """Gets permission levels"""
        return list(self)
