from __future__ import annotations
from typing import TYPE_CHECKING, ClassVar, Any, Optional

from dataclasses import asdict, dataclass, field

import discord

from ..enums import EmbedMediaType
from .. import utils

if TYPE_CHECKING:
    from typing_extensions import Self
    from .._types import PossibleData, SupportsCastingToString

    from .media import EmbedMedia


@dataclass(**utils.KW_ONLY_DATACLASS)
class BaseEmbedDataclass:
    def __call__(self, *args: Any, **kwargs: Any):
        return self.from_dict(*args, **kwargs)

    @classmethod
    def from_dict(cls, data: PossibleData) -> Self:
        return cls(**data)

    def to_dict(self) -> PossibleData:
        return {key: str(value) if not isinstance(value, bool) else value for key, value in asdict(self).items() if value is not None}  # type: ignore

    def replace(self, **kwargs: Any) -> Self:
        for attr, value in kwargs.items():
            if attr not in self.__dict__:
                raise AttributeError(f"{attr} is not an attribute of {self.__class__.__name__}")

            setattr(self, attr, value)

        return self


@dataclass(**utils.KW_ONLY_DATACLASS)
class WithIconURL(BaseEmbedDataclass):
    media_type: ClassVar[EmbedMediaType]
    icon_url: Optional[SupportsCastingToString] = None
    icon_file: Optional[discord.File] = None
    proxy_icon_url: Optional[str] = field(default=None, init=False)

    def __post_init__(self):
        # circular import
        from .media import EmbedMedia

        if self.icon_url:
            self.icon_url = str(self.icon_url)

        if self.icon_file:
            self.icon_url = EmbedMedia.URL_WITH_FILE_PLACEHOLDER.format(self.icon_file.filename)

        del EmbedMedia

    @discord.utils.cached_property
    def media(self) -> Optional[EmbedMedia]:
        if not self.icon_url or not self.icon_file:
            return None

        # circular import
        from .media import EmbedMedia

        inst = EmbedMedia(
            media_type=self.media_type,
            url=self.icon_url,
            file=self.icon_file,
        )
        if self.proxy_icon_url:
            inst.proxy_url = self.proxy_icon_url

        del EmbedMedia
        return inst
