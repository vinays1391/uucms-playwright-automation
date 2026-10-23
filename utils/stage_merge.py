"""Deep-merge helper for layered Ph.D admission stage data."""

from collections.abc import Mapping


def deep_merge(base: Mapping, override: Mapping) -> dict:
    """Merge ``override`` on top of ``base`` without mutating either input.

    Nested dicts are merged key by key; lists and scalars are replaced
    wholesale. Used to layer candidate-specific values over group and
    shared stage templates.
    """
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
