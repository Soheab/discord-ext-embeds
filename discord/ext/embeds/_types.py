from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Protocol, Sized, Tuple, Type, TypedDict, Union

if TYPE_CHECKING:
    from typing_extensions import NotRequired
    from .models import *

    from discord import Message, PartialMessage, WebhookMessage, InteractionMessage
    from discord.types.embed import (
        Embed as EmbedData,
        EmbedField as EmbedFieldData,
        EmbedFooter as EmbedFooterData,
        EmbedAuthor as EmbedAuthorData,
        EmbedProvider as EmbedProviderData,
        EmbedMedia as EmbedMediaData,
    )

__all__ = ()


class SupportsCastingToString(Protocol[Sized]):
    def __str__(self) -> str: ...

    def __len__(self) -> int: ...


class FieldDict(TypedDict):
    name: str
    value: str
    inline: NotRequired[bool]
    index: NotRequired[int]


Field_NameValue = Tuple[str, str]
Field_NameValueInline = Tuple[str, str, bool]
Field_NameValueInlineIndex = Tuple[str, str, bool, int]
Field_NameValueIndex = Tuple[str, str, int]


Field_Values = Union[
    Field_NameValue, Field_NameValueInline, Field_NameValueInlineIndex, Field_NameValueIndex, FieldDict
]

PossibleData = Union[
    "EmbedAuthorData",
    "EmbedFooterData",
    "EmbedFieldData",
    "EmbedData",
    "EmbedProviderData",
]
PossibleClassTypes = Type[  # noqa: F405
    Union[
        "EmbedFooter",
        "EmbedField",
        "EmbedAuthor",
        "EmbedProvider",
        "EmbedMedia",
        "EmbedFields",
    ]
]
MediaTypes = Literal["image", "video", "thumbnail", "icon_url"]


class EmbedMediaDataDictReturnValue(TypedDict):
    url: str
    flags: NotRequired[int]


EmbedMediaDataDictReturn = dict[MediaTypes, EmbedMediaDataDictReturnValue]

PossibleMessage = Union[
    InteractionMessage,
    WebhookMessage,
    Message,
    PartialMessage,
]
