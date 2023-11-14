from __future__ import annotations
from typing import TYPE_CHECKING, Union, Any

from dataclasses import is_dataclass, make_dataclass, dataclass as _dataclass

if TYPE_CHECKING:
    from ._types import PossibleData, EmbedMediaData

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
    del attr_to_class
    if not value:
        NAME = str(cls).split(".")[-1][:-2]
        return _create_dataclass(NAME, value)  # type: ignore

    return cls.from_dict(value)  # type: ignore


def _create_dataclass(class_name: str, fields: dict[str, Any]):
    main_instance = make_dataclass(
        class_name,
        list(fields.keys()),
        namespace={"__getattr__": lambda __, _: None},  # type: ignore
        **KW_ONLY_DATACLASS,  # type: ignore
    )
    return main_instance(**fields)
