from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any, TypeAlias

MetadataScalar: TypeAlias = str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class MetadataEntry:
    """One immutable, ordered metadata entry."""

    key: str
    value: FrozenMetadataValue

    def __post_init__(self) -> None:
        _validate_key(self.key)
        object.__setattr__(self, "value", freeze_metadata_value(self.value))


@dataclass(frozen=True, slots=True)
class FrozenMetadataMap(Mapping[str, Any]):
    """Small immutable mapping backed by an ordered tuple of entries."""

    entries: tuple[MetadataEntry, ...] = ()

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for entry in self.entries:
            if not isinstance(entry, MetadataEntry):
                raise TypeError("Metadata entries must be MetadataEntry values.")
            if entry.key in seen:
                raise ValueError(f"Duplicate metadata key: {entry.key!r}.")
            seen.add(entry.key)

    def __getitem__(self, key: str) -> FrozenMetadataValue:
        for entry in self.entries:
            if entry.key == key:
                return entry.value
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return (entry.key for entry in self.entries)

    def __len__(self) -> int:
        return len(self.entries)


FrozenMetadataValue: TypeAlias = (
    MetadataScalar | tuple["FrozenMetadataValue", ...] | FrozenMetadataMap
)


def freeze_metadata(
    metadata: Mapping[str, Any] | tuple[MetadataEntry, ...] | None,
) -> tuple[MetadataEntry, ...]:
    """Normalize metadata into an ordered, deeply immutable tuple."""

    if metadata is None:
        return ()
    if isinstance(metadata, tuple):
        if not all(isinstance(entry, MetadataEntry) for entry in metadata):
            raise TypeError(
                "ModelSchema metadata tuples must contain MetadataEntry values."
            )
        source = ((entry.key, entry.value) for entry in metadata)
    elif isinstance(metadata, Mapping):
        source = metadata.items()
    else:
        raise TypeError(
            "ModelSchema metadata must be a mapping, a metadata-entry tuple, or None."
        )

    entries: list[MetadataEntry] = []
    seen: set[str] = set()
    for key, value in source:
        _validate_key(key)
        if key in seen:
            raise ValueError(f"Duplicate metadata key: {key!r}.")
        seen.add(key)
        entries.append(MetadataEntry(key=key, value=freeze_metadata_value(value)))
    return tuple(entries)


def freeze_metadata_value(value: Any) -> FrozenMetadataValue:
    """Recursively detach metadata from mutable framework-owned values."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, FrozenMetadataMap):
        return value
    if isinstance(value, Mapping):
        return FrozenMetadataMap(freeze_metadata(value))
    if isinstance(value, (list, tuple)):
        return tuple(freeze_metadata_value(item) for item in value)

    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        normalized = tolist()
        if normalized is not value:
            return freeze_metadata_value(normalized)

    item = getattr(value, "item", None)
    if callable(item):
        normalized = item()
        if normalized is not value:
            return freeze_metadata_value(normalized)

    raise TypeError(
        "ModelSchema metadata values must normalize to immutable scalar, "
        "sequence, or string-keyed mapping values; got "
        f"{type(value).__name__}."
    )


def thaw_metadata(entries: tuple[MetadataEntry, ...]) -> dict[str, Any]:
    """Return a detached built-in representation for reports/serialization."""

    return {entry.key: thaw_metadata_value(entry.value) for entry in entries}


def thaw_metadata_value(value: FrozenMetadataValue) -> Any:
    if isinstance(value, FrozenMetadataMap):
        return thaw_metadata(value.entries)
    if isinstance(value, tuple):
        return [thaw_metadata_value(item) for item in value]
    return value


def _validate_key(key: object) -> None:
    if not isinstance(key, str):
        raise TypeError("Metadata keys must be strings.")
    if not key:
        raise ValueError("Metadata keys cannot be empty.")
    if key.strip() != key:
        raise ValueError("Metadata keys cannot have leading or trailing whitespace.")
