from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass

from .base import BaseEmbedDataclass

if TYPE_CHECKING:
    from typing_extensions import Self

    from discord.types.embed import EmbedProvider as EmbedProviderData

__all__ = ("EmbedProvider",)


@dataclass(eq=False)
class EmbedProvider(BaseEmbedDataclass):
    """Represents an embed provider.

    See the docs for more info: https://discord.com/developers/docs/resources/channel#embed-object-embed-types

    Parameters
    ----------
    name: :class:`str`
        The name of the provider.
    url: :class:`str`
        The URL of the provider.
    """

    name: str
    url: str

    @classmethod
    def from_dict(cls, data: EmbedProviderData) -> Self:
        return cls(**data)
