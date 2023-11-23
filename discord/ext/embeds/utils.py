from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union, Any, Literal

from dataclasses import is_dataclass, make_dataclass, dataclass as _dataclass

import discord

if TYPE_CHECKING:
    from ._types import PossibleData, EmbedMediaData, SupportsCastingToString

__all__ = ()

# kw_only is only available in Python 3.10+
KW_ONLY_DATACLASS = dict(kw_only=True) if "kw_only" in _dataclass.__kwdefaults__ else {}


def _maybe_construct(name: str, value: Union[PossibleData, EmbedMediaData, Any]) -> Any:  # type: ignore # it's an internal function, so it's fine
    if name == "_fields":
        return value

    if is_dataclass(value):
        return value

    # circular import
    from .embeds import attr_to_class

    cls = attr_to_class[name]

    if cls and not value:
        return _create_dataclass(cls.__name__, {})
    elif not cls:
        return _create_dataclass(name.casefold(), value)  # type: ignore

    del attr_to_class
    return cls.from_dict(value)  # type: ignore


def _create_dataclass(class_name: str, fields: dict[str, Any]):
    def proxy_getattr(_s: Any, _n: str) -> None:
        return None

    def proxy_len(_s: Any) -> int:
        return 0

    def proxy_bool(_s: Any) -> bool:
        return False

    main_instance = make_dataclass(
        class_name,
        list(fields.keys()),
        namespace={"__getattr__": proxy_getattr, "__len__": proxy_len, "__bool__": proxy_bool},
        **KW_ONLY_DATACLASS,  # type: ignore
    )
    return main_instance(**fields)


def handle_colour(
    data: dict[Literal["color", "colour"], Optional[Union[int, SupportsCastingToString, discord.Colour]]]
) -> Optional[discord.Colour]:
    value = data.get("color", data.get("colour"))

    if isinstance(value, int):
        return discord.Colour(value=value)
    elif isinstance(value, str):
        return discord.Colour.from_str(value)
    elif isinstance(value, discord.Colour):
        return value
    else:
        raise TypeError(f"Expected int, str or discord.Colour, got {value.__class__.__name__} instead.")
