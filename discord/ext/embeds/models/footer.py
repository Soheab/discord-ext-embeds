from __future__ import annotations

from typing import TYPE_CHECKING, Optional, ClassVar
from dataclasses import dataclass, field

import discord

from .base import WithIconURL
from ..enums import EmbedMediaType

if TYPE_CHECKING:
    from .._types import SupportsCastingToString

__all__ = ("EmbedFooter",)


@dataclass
class EmbedFooter(WithIconURL):
    """Represents an embed footer.

    Parameters
    ----------
    text: :class:`str`
        The text of the footer.
    icon_url: Optional[:class:`str`]
        The icon URL of the footer.
    icon_file: Optional[:class:`discord.File`]
        The icon file of the footer. This cannot be used with ``icon_url``.
    """

    # using default_factory here is an easy workaround
    # see https://stackoverflow.com/a/73095470 for more.
    text: SupportsCastingToString = field(default_factory=str)
    """The text of the footer."""
    media_type: ClassVar[EmbedMediaType] = EmbedMediaType.footer_icon
    """The media type of the footer."""
    icon_url: Optional[SupportsCastingToString] = None
    """The icon URL of the footer. This cannot be used with ``icon_file``."""
    icon_file: Optional[discord.File] = None
    """The icon file of the footer. This cannot be used with ``icon_url``."""
    proxy_icon_url: Optional[str] = field(default=None, init=False)
    """The proxy icon URL of the footer."""

    def __post_init__(self):
        self.text = str(self.text)
        super().__post_init__()

    def __len__(self) -> int:
        return len(self.text)

    def __bool__(self) -> bool:
        return bool(self.text)
