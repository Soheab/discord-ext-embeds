from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from discord import DiscordException

if TYPE_CHECKING:
    from .models.base import BaseEmbedDataclass

__all__ = ("LimitReached",)


class LimitReached(DiscordException):
    """Exception raised when the maximum number of x is reached.
    
    Parameters
    ----------
    limit_of: :class:`str`
        The limit of what was reached.
    limit: :class:`int`
        The limit of the object.
    current: :class:`int`
        The current amount of the object.
    object: Optional[:class:`BaseEmbedDataclass`]
        The related object. If any.
    field_index: Optional[:class:`int`]
        The index of the field that was reached. If any.
    """

    def __init__(
        self,
        limit_of: str,
        limit: int,
        current: int,
        *,
        object: Optional[BaseEmbedDataclass] = None,
        field_index: Optional[int] = None,
    ) -> None:
        self.limit_of: str = limit_of
        self.object: Optional[BaseEmbedDataclass] = object
        self.limit: int = limit
        self.current: int = current

        KWARG_INFO = "You can set check_limits to False in Embed() to disable this check."
        DISCLAIMER = (
            "Note that the limit is hardcoded and may have changed since the last update. "
            f"Please open an issue if you think this is the case. Thank you!\n{KWARG_INFO}"
        )
        OBJECT = f" ({self.object})" if self.object is not None else ""
        INDEX = f" at index {field_index}" if field_index is not None else ""
        super().__init__(f"The limit of {limit_of}{OBJECT}{INDEX} was reached ({current}/{limit}).\nDisclaimer: {DISCLAIMER}")
