from __future__ import annotations
from typing import TYPE_CHECKING, Literal, NotRequired, Protocol, Tuple, Type, TypedDict, Union, type_check_only

if TYPE_CHECKING:
    from .models import *

    from discord import Message, PartialMessage, WebhookMessage, InteractionMessage
    from discord.types.embed import (
        Embed as EmbedData,
        EmbedField as EmbedFieldData,
        EmbedFooter as EmbedFooterData,
        EmbedAuthor as EmbedAuthorData,
        EmbedProvider as EmbedProviderData,
        EmbedImage as EmbedImageData,
        EmbedVideo as EmbedVideoData,
        EmbedThumbnail as EmbedThumbnailData,
    )


@type_check_only
class SupportsCastingToString(Protocol):
    def __str__(self) -> str:
        ...


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
EmbedMediaData = Union["EmbedImageData", "EmbedVideoData", "EmbedThumbnailData"]
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
MediaTypes = Literal["image", "video", "thumbnail"]
EmbedMediaDataDictReturn = dict[MediaTypes, dict[Literal["url"], str]]

PossibleMessage = Union[
    InteractionMessage,
    WebhookMessage,
    Message,
    PartialMessage,
]
