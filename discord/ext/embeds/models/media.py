from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    ClassVar,
    Union,
)
from dataclasses import dataclass, field
import re

from ..enums import EmbedMediaType

import discord

if TYPE_CHECKING:
    from typing_extensions import Self

    from .._types import (
        EmbedMediaDataDictReturn,
        EmbedMediaData,
        SupportsCastingToString,
    )


__all__ = ("EmbedMedia",)


@dataclass()
class EmbedMedia:
    """Represents an embed media.

    Parameters
    ----------
    media_type: EmbedMediaType
        The type of media.
    url: :class:`str`
        The URL of the media.
    check_url: :class:`bool`
        Whether to check if the URL is valid. Defaults to ``True``.
    file: Optional[:class:`discord.File`]
        The file of the media.

    Attributes
    ----------
    media_type: EmbedMediaType
        The type of media.
    url: :class:`str`
        The URL of the media.
    check_url: :class:`bool`
        Whether to URL was checked.
    proxy_url: Optional[:class:`str`]
        The proxy URL of the media.
    height: Optional[:class:`int`]
        The height of the media.
    width: Optional[:class:`int`]
        The width of the media.
    flags: :class:`discord.AttachmentFlags`
        The flags of the media.

    Raises
    ------
    ValueError
        Invalid type or media type passed or invalid URL passed (if ``check_url`` is ``True``).
    """

    URL_WITH_FILE_PLACEHOLDER: ClassVar[str] = "attachment://{filename}"
    URL_REGEX: ClassVar[re.Pattern[str]] = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    media_type: EmbedMediaType
    """The type of media."""
    file: Optional[discord.File] = field(default=None, repr=False)
    """The file of the media."""
    url: Optional[SupportsCastingToString] = field(default=None)
    """The URL of the media."""
    check_url: bool = field(default=True, repr=False)
    """Whether to check if the URL is valid. Defaults to ``True``."""
    proxy_url: Optional[str] = field(default=None, repr=False, init=False)
    """The proxy URL of the media."""
    height: Optional[int] = field(default=None, repr=False, init=False)
    """The height of the media."""
    width: Optional[int] = field(default=None, repr=False, init=False)
    """The width of the media."""

    _flags: int = field(default=0, repr=False, init=False)
    """The flags of the media."""

    def __post_init__(self) -> None:
        if not self.url and not self.file:
            raise ValueError("Either url or file must be passed.")

        if self.url and self.check_url and not str(self.url).startswith("attachment://"):
            if not self.URL_REGEX.match(str(self.url)):
                raise ValueError(f"Invalid {self.media_type} URL {self.url!r}")

            self.url = str(self.url)

        if not isinstance(self.media_type, EmbedMediaType):
            raise ValueError(f"Invalid media type. Expected EmbedMediaType, got {self.media_type!r}")

        if self.file:
            self.url = self.URL_WITH_FILE_PLACEHOLDER.format(filename=self.file.filename)

    def __bool__(self) -> bool:
        return bool(self.url or self.file)

    def replace(self, **kwargs: Any) -> Self:
        for attr, value in kwargs.items():
            if attr not in self.__annotations__:
                raise AttributeError(f"{attr} is not an attribute of {self.__class__.__name__}")

            if attr.startswith("_"):
                raise AttributeError(f"{attr} is a private attribute of {self.__class__.__name__}. They cannot be set.")

            setattr(self, attr, value)

        return self

    def to_dict(self) -> EmbedMediaDataDictReturn:
        """Converts this media to a dict.

        Returns
        -------
        :class:`dict`
            The dict representation of this media.
        """
        data: dict[str, str | int] = {"url": self.url}  # type: ignore
        _type = self.media_type.value
        if _type in ("footer_icon", "author_icon"):
            _type = "icon_url"
        else:
            data["flags"] = self._flags

        return {_type: data}  # type: ignore

    @property
    def flags(self) -> discord.AttachmentFlags:
        """The flags of the media.

        .. versionadded:: 2.5
        """
        return discord.AttachmentFlags._from_value(self._flags)

    @classmethod
    def from_dict(cls, data: EmbedMediaData) -> Self:
        """Creates a media from a dict.

        Parameters
        ----------
        data: :class:`dict`
            The dict representation of the media.
            A ``"media_type"`` key is required.
        """
        media_type = data["media_type"]  # type: ignore
        if isinstance(media_type, str):
            media_type = EmbedMediaType[media_type.lower()]

        cls_attrs = {"media_type": media_type, "url": data["url"]}  # type: ignore
        inst = cls(**cls_attrs)  # type: ignore
        if inst.media_type in (EmbedMediaType.image, EmbedMediaType.video, EmbedMediaType.thumbnail):
            inst = inst.replace(
                height=data.get("height"),
                width=data.get("width"),
                proxy_url=data.get("proxy_url"),
            )

        inst._flags = data.get("flags", 0)

        return inst

    @classmethod
    def construct(
        cls,
        media_type: EmbedMediaType,
        value: Union[SupportsCastingToString, discord.File, EmbedMediaData, EmbedMedia],
    ) -> Self:
        if isinstance(value, cls):
            return value

        kwargs: dict[str, Any] = {"media_type": media_type}
        if isinstance(value, discord.File):
            kwargs["file"] = value
        else:
            kwargs["url"] = value

        inst = cls(**kwargs)
        if isinstance(value, dict):
            if "flags" in value:
                inst._flags = value["flags"]

            if "proxy_url" in value:
                inst.proxy_url = value["proxy_url"]

            if "height" in value:
                inst.height = value["height"]

            if "width" in value:
                inst.width = value["width"]

        return inst
