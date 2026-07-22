from __future__ import annotations

import hashlib
import json
import math
from dataclasses import fields, is_dataclass
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from dsl.provenance.model import ContentFingerprint


class CanonicalizationError(TypeError):
    """Raised when a value has no stable FORML canonical representation."""


def canonicalize(value: Any) -> Any:
    """Return a deterministic, type-preserving JSON-ready representation."""

    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, float):
        if math.isnan(value):
            payload = "nan"
        elif math.isinf(value):
            payload = "+inf" if value > 0 else "-inf"
        else:
            payload = value.hex()
        return {"$type": "float", "value": payload}
    if isinstance(value, Decimal):
        if value.is_nan():
            payload = "snan" if value.is_snan() else "nan"
            if value.is_signed():
                payload = "-" + payload
            return {"$type": "decimal", "value": payload}
        if value.is_infinite():
            return {
                "$type": "decimal",
                "value": "-inf" if value.is_signed() else "+inf",
            }
        parts = value.as_tuple()
        return {
            "$type": "decimal",
            "sign": parts.sign,
            "digits": "".join(str(digit) for digit in parts.digits) or "0",
            "exponent": parts.exponent,
        }
    if isinstance(value, bytes):
        return {"$type": "bytes", "hex": value.hex()}
    if isinstance(value, Path):
        return {"$type": "path", "value": value.as_posix()}
    if isinstance(value, Enum):
        return {
            "$type": "enum",
            "class": f"{type(value).__module__}.{type(value).__qualname__}",
            "value": canonicalize(value.value),
        }
    if is_dataclass(value) and not isinstance(value, type):
        return {
            "$type": "dataclass",
            "class": f"{type(value).__module__}.{type(value).__qualname__}",
            "fields": {
                item.name: canonicalize(getattr(value, item.name))
                for item in fields(value)
            },
        }
    if isinstance(value, Mapping):
        items = [
            (canonical_json_bytes(key), canonicalize(key), canonicalize(item))
            for key, item in value.items()
        ]
        items.sort(key=lambda entry: entry[0])
        return {"$type": "mapping", "items": [[key, item] for _, key, item in items]}
    if isinstance(value, (set, frozenset)):
        items = [canonicalize(item) for item in value]
        items.sort(key=canonical_json_bytes)
        return {"$type": "set", "items": items}
    if isinstance(value, tuple):
        return {"$type": "tuple", "items": [canonicalize(item) for item in value]}
    if isinstance(value, list):
        return {"$type": "list", "items": [canonicalize(item) for item in value]}

    item_method = getattr(value, "item", None)
    if callable(item_method):
        try:
            item = item_method()
        except (TypeError, ValueError):
            pass
        else:
            if item is not value:
                return {
                    "$type": f"scalar:{type(value).__module__}.{type(value).__qualname__}",
                    "value": canonicalize(item),
                }

    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        try:
            items = tolist()
        except (TypeError, ValueError):
            pass
        else:
            return {
                "$type": f"array:{type(value).__module__}.{type(value).__qualname__}",
                "value": canonicalize(items),
            }

    raise CanonicalizationError(
        "No stable canonical representation for "
        f"{type(value).__module__}.{type(value).__qualname__}"
    )


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        canonicalize(value),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def fingerprint_bytes(
    data: bytes,
    *,
    canonicalization: str,
) -> ContentFingerprint:
    return ContentFingerprint(
        algorithm="sha256",
        digest=hashlib.sha256(data).hexdigest(),
        size_bytes=len(data),
        canonicalization=canonicalization,
    )


def fingerprint_text(text: str) -> ContentFingerprint:
    return fingerprint_bytes(
        text.encode("utf-8"),
        canonicalization="utf8_compiler_source",
    )


def fingerprint_file(path: str | Path) -> ContentFingerprint:
    resolved = Path(path)
    return fingerprint_bytes(
        resolved.read_bytes(),
        canonicalization="raw_file_bytes",
    )


def fingerprint_canonical_json(
    value: Any,
    *,
    canonicalization: str,
) -> ContentFingerprint:
    return fingerprint_bytes(
        canonical_json_bytes(value),
        canonicalization=canonicalization,
    )
