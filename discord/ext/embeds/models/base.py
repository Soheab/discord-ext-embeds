from __future__ import annotations
from typing import TYPE_CHECKING, ClassVar, Any, Literal, Optional, Union

from reprlib import recursive_repr

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

    @recursive_repr()
    def __repr__(self) -> str:
        human_attrs = ", ".join(f"{attr}={value!r}" for attr, value in self.__dict__.items())
        return f"<{self.__class__.__name__} {human_attrs}>"

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

    @classmethod
    def from_user(cls, user: Union[discord.Member, discord.User]) -> WithIconURL:
        """Create an instance of this class from a :class:`~discord.User` or :class:`~discord.Member` object.

        This method will attempt to use the ``name`` or ``text`` field of the class to set the user's display name
        and the ``icon_url`` field to set the user's display_avatar.
        Parameters
        ----------
        user: Union[discord.Member, discord.User]
            The user to create the instance from.
        """
        all_fields = cls.__dataclass_fields__

        name = user.display_name
        avatar_url = user.display_avatar.url

        kwargs: dict[Literal["name", "text", "icon_url"], str] = {
            "icon_url": avatar_url,
        }
        if "name" in all_fields:
            kwargs["name"] = name
        elif "text" in all_fields:
            kwargs["text"] = name
        else:
            raise TypeError("Cannot determine which field to use for the user's display name")

        return cls(**kwargs)  # type: ignore # not sure why this is an error, not even using icon_file

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
