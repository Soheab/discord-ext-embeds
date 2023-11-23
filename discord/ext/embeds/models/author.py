from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Optional
from dataclasses import dataclass, field

import discord

from .base import WithIconURL
from ..enums import EmbedMediaType

if TYPE_CHECKING:
    from .._types import SupportsCastingToString


__all__ = ("EmbedAuthor",)


@dataclass
class EmbedAuthor(WithIconURL):
    """Represents an embed author.

    Parameters
    ----------
    name: :class:`str`
        The name of the author.
    url: Optional[:class:`str`]
        The URL of the author.
    icon_url: Optional[:class:`str`]
        The icon URL of the author.
    icon_file: Optional[:class:`discord.File`]
        The icon file of the author. This cannot be used with ``icon_url``.
    """

    # using default_factory here is an easy workaround
    # see https://stackoverflow.com/a/73095470 for more.
    name: SupportsCastingToString = field(default_factory=str)
    """The name of the author."""
    media_type: ClassVar[EmbedMediaType] = EmbedMediaType.author_icon
    """The media type of the author."""

    url: Optional[str] = None
    """The URL of the author."""
    icon_url: Optional[SupportsCastingToString] = None
    """The icon URL of the author."""
    icon_file: Optional[discord.File] = None
    """The icon file of the author. This cannot be used with ``icon_url``."""
    proxy_icon_url: Optional[str] = field(default=None, init=False)
    """The proxy icon URL of the author."""

    def __post_init__(self):
        self.name = str(self.name)
        self.url = str(self.url) if self.url else None
        super().__post_init__()

    def __len__(self) -> int:
        return len(self.name)

    def __bool__(self) -> bool:
        return bool(self.name)
