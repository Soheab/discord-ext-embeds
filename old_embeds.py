from __future__ import annotations
import re
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Literal,
    Protocol,
    Sequence,
    Type,
    TypeVar,
    Union,
    Optional,
    get_type_hints,
    overload,
    NamedTuple,
)

from enum import Enum
from copy import deepcopy
from functools import partial
from datetime import datetime, timezone

from dataclasses import is_dataclass

import discord
from discord.abc import Messageable
from discord.ext import commands


from .models import (
    EmbedField,
    EmbedFields,
    EmbedAuthor,
    EmbedFooter,
    EmbedMedia,
    EmbedProvider,
)
from .enums import EmbedMediaType
from . import utils


if TYPE_CHECKING:
    from typing_extensions import Self

    from discord.types.embed import (
        Embed as EmbedData,
        EmbedType as EmbedTypeData,
        EmbedField as EmbedFieldData,
    )

    from ._types import (
        PossibleMessage,
    )

    class SetImageThumbnailFunc(Protocol):
        def __call__(self, *, url: Optional[str]) -> Self:
            r"""set_image/thumbnail(\*, url=...)

            Parameters
            ----------
            url: Optional[:class:`str`]
                The URL of the image/thumbnail. ``None`` to remove.

            Returns
            -------
            :class:`Embed`
                The embed object.
            """
            ...

    class SetAuthorFunc(Protocol):
        def __call__(
            self,
            *,
            name: str,
            url: Optional[str] = None,
            icon_url: Optional[str] = None,
        ) -> Self:
            r"""set_author(\*, name, url=None icon_url=None)

            Parameters
            ----------
            name: :class:`str`
                The name of the author.
            url: Optional[:class:`str`]
                The URL of the author.
            icon_url: Optional[:class:`str`]
                The URL of the author's icon.

            Returns
            -------
            :class:`Embed`
                The embed object.
            """
            ...

    class SetFooterFunc(Protocol):
        def __call__(self, *, text: str, icon_url: Optional[str] = None) -> Self:
            r"""set_footer(\*, text, icon_url=None)

            Parameters
            ----------
            text: :class:`str`
                The text of the footer.
            icon_url: Optional[:class:`str`]
                The URL of the footer's icon.

            Returns
            -------
            :class:`Embed`
                The embed object.
            """
            ...

    Field_NameValue = tuple[str, str]
    Field_NameValueInline = tuple[str, str, bool]
    Field_NameValueInlineIndex = tuple[str, str, bool, int]
    Field_NameValueIndex = tuple[str, str, int]

    Field_Values = Union[
        Field_NameValue,
        Field_NameValueInline,
        Field_NameValueInlineIndex,
        Field_NameValueIndex,
    ]

    Interaction = discord.Interaction[Any]
    Context = commands.Context[Any]

__all__ = ("Embed", "EmbedField", "EmbedFooter", "EmbedAuthor")


MISSING = discord.utils.MISSING


class _EmbedLimits(NamedTuple):
    title: int
    description: int
    fields: int
    field_name: int
    field_value: int
    footer_text: int
    author_name: int


# https://discord.com/developers/docs/resources/channel#embed-object
# 10 November, 2023
EMBED_LIMITS = _EmbedLimits(
    title=256,
    description=4096,
    fields=25,
    field_name=256,
    field_value=1024,
    footer_text=2048,
    author_name=256,
)


class DEFAULT_VALUE:
    default: Optional[Any]

    def __init__(self, default: Optional[Any]) -> None:
        self.default = default

    def value(self, value: Optional[Any]) -> Any:
        if value is None:
            return None
        elif value is MISSING:
            return self.default
        elif self.default is MISSING:
            return value
        else:
            return value


class SetFuncType(Enum):
    IMAGE = "image"
    THUMBNAIL = "thumbnail"
    AUTHOR = "author"
    FOOTER = "footer"

    def __str__(self) -> str:
        return self.value


PossibleSetFunc = Union["SetImageThumbnailFunc", "SetAuthorFunc", "SetFooterFunc"]


@overload
def _is_set_function(
    _type: Literal[SetFuncType.IMAGE, SetFuncType.THUMBNAIL]
) -> Callable[[Callable], SetImageThumbnailFunc]:
    ...


@overload
def _is_set_function(
    _type: Literal[SetFuncType.AUTHOR],
) -> Callable[[Callable], SetAuthorFunc]:
    ...


@overload
def _is_set_function(
    _type: Literal[SetFuncType.FOOTER],
) -> Callable[[Callable], SetFooterFunc]:
    ...


def _is_set_function(_type: SetFuncType) -> Callable[[Callable], PossibleSetFunc]:
    def decorator(func: Callable) -> PossibleSetFunc:
        func.__is_set_func__ = _type
        return func

    return decorator


if TYPE_CHECKING:
    from typing_extensions import TypeVar

    TitleT = TypeVar("TitleT", bound=Optional[str], default=None)
    DescriptionT = TypeVar("DescriptionT", bound=Optional[str], default=None)
else:
    TitleT = TypeVar("TitleT", bound=Optional[str], covariant=True)
    DescriptionT = TypeVar("DescriptionT", bound=Optional[str], covariant=True)


class Embed(Generic[TitleT, DescriptionT]):
    _fields: EmbedFields

    __user_attributes__: tuple[str, ...] = (
        "title",
        "description",
        "url",
        "_colour",
        "_color",
        "_timestamp",
        "_image",
        "_thumbnail",
        "_footer",
        "_author",
        "_video",
        "_provider",
    )
    __slots__ = (
        "title",
        "url",
        "type",
        "description",
        "_colour",
        "_timestamp",
        "_fields",
        "_image",
        "_thumbnail",
        "_footer",
        "_author",
        "_video",
        "_provider",
        "_check_limits",
        "_author_object",
    )

    def __init__(
        self,
        *,
        title: TitleT = None,
        description: DescriptionT = None,
        colour: Optional[Union[int, discord.Colour, None]] = MISSING,
        color: Optional[Union[int, discord.Colour, None]] = MISSING,
        url: Optional[Any] = None,
        timestamp: Optional[datetime] = None,
        image: Optional[Any] = None,
        fields: list[EmbedField] = [],
        thumbnail: Optional[Any] = None,
        footer: Optional[Union[str, EmbedFooter]] = None,
        author: Optional[EmbedAuthor] = MISSING,
        check_limits: bool = True,
        author_object: Optional[Union[discord.Member, discord.User]] = None,
    ) -> None:
        self._check_limits = check_limits
        self._author_object: Optional[
            Union[discord.Member, discord.User]
        ] = author_object

        self.type: EmbedTypeData = "rich"

        self.title = title
        if self.title is not None:
            self.title = str(title)

        self.description = description
        if self.description is not None:
            self.description = str(description)

        self.url = url
        if self.url is not None:
            self.url = str(url)

        if timestamp is not None:
            self.timestamp = timestamp
        # .....................
        # self.colour = colour if colour is not MISSING else color

        if fields:
            self.fields = fields

        if image is not None:
            self.image = image

        if thumbnail is not None:
            self.thumbnail = thumbnail

        if footer is not None:
            self.footer = footer

        self._set_default_author(author)
        self._set_default_colour(colour if colour is not MISSING else color)

    def _set_default_author(self, author: Optional[EmbedAuthor]) -> None:
        default_author = MISSING
        if self._author_object is not None:
            default_author = EmbedAuthor(
                name=self._author_object.display_name,
                icon_url=self._author_object.display_avatar.url,
            )
        
        to_set = utils._handle_default(default_author, author)
        if to_set in (None, MISSING):
            return

        self.author = to_set

    def _set_default_colour(
        self, colour: Optional[Union[int, discord.Colour, None]]
    ) -> None:
        self.colour = utils._handle_default(discord.Colour.dark_theme(), colour)

    def __str__(self) -> str:
        return self.title or ""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(title={self.title!r} color={self.color!r} url={self.url!r} timestamp={self.timestamp!r})"

    def __delattr__(self, __name: str) -> None:
        try:
            VALID_SET_FUNCS = get_type_hints(self.__handle_set_)["_type"].__args__
            VALID_NAMES: tuple[str, ...] = (
                "colour",
                "timestamp",
                "fields",
            ) + VALID_SET_FUNCS
        except AttributeError:
            VALID_NAMES = ("colour", "timestamp", "fields")  # type: ignore
            VALID_SET_FUNCS = ()
        if __name in VALID_NAMES:
            try:
                if __name in VALID_SET_FUNCS:
                    delattr(self, f"set_{__name}")
                delattr(self, f"_{__name}")
            except AttributeError:
                pass
        else:
            super().__delattr__(__name)

    def __getattribute__(self, __name: str):
        try:
            attr = object.__getattribute__(self, __name)
        except AttributeError:
            raise AttributeError(
                f"{self.__class__.__name__} object has no attribute {__name!r}"
            )
        else:
            if set_type := getattr(attr, "__is_set_func__", None):
                return partial(
                    object.__getattribute__(
                        self, f"_{self.__class__.__name__}__handle_set_"
                    ),
                    set_type,
                )
            else:
                return attr

    def __handle_set_(self, _type: SetFuncType, **kwargs):  # type: ignore
        FULL_ATTR_NAME = f"_{_type}"

        EXAMPLES: dict[SetFuncType, str] = {
            SetFuncType.THUMBNAIL: "url=...",
            SetFuncType.IMAGE: "url=...",
            SetFuncType.FOOTER: "text=..., icon_url=...",
            SetFuncType.AUTHOR: "name=..., url=..., icon_url=...",
        }
        if not kwargs:
            raise ValueError(
                f"No keyword arguments passed to set{FULL_ATTR_NAME}. Use it like this: ...set{FULL_ATTR_NAME}({EXAMPLES[_type]})"
            )

        if (
            _type in (SetFuncType.IMAGE, SetFuncType.THUMBNAIL)
            and "url" in kwargs
            and kwargs["url"] is None
        ):
            try:
                delattr(self, FULL_ATTR_NAME)
            except AttributeError:
                pass

            return self

        if _type in (SetFuncType.IMAGE, SetFuncType.THUMBNAIL):
            kwargs: EmbedMediaDataDictReturn = {"_type": _type.value.lower(), **kwargs}  # type: ignore

        try:
            data_class = attr_to_class[_type.value.lower()].from_dict(kwargs)  # type: ignore
        except TypeError as err:
            if "__init__() got an unexpected keyword argument" in str(err):
                raise ValueError(
                    f"Invalid keyword arguments passed to set{FULL_ATTR_NAME}. Use it like this: ...set{FULL_ATTR_NAME}({EXAMPLES[_type]})"
                )
            else:
                raise err
        else:
            setattr(self, FULL_ATTR_NAME, data_class)  # type: ignore

        return self

    @_is_set_function(SetFuncType.IMAGE)
    def set_image(self) -> Self:
        ...

    @_is_set_function(SetFuncType.THUMBNAIL)
    def set_thumbnail(self) -> Self:
        ...

    @_is_set_function(SetFuncType.FOOTER)
    def set_footer(self) -> Self:
        ...

    @_is_set_function(SetFuncType.AUTHOR)
    def set_author(self) -> Self:
        ...

    async def send(
        self,
        destination: Union[Messageable, Interaction],
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[PossibleMessage]:
        if isinstance(destination, Messageable):
            send_method = destination.send
        elif isinstance(destination, discord.Interaction):
            if not destination.response.is_done():
                send_method = destination.response.send_message
            else:
                send_method = destination.followup.send
        elif isinstance(destination, Messageable):
            send_method = destination.send
        else:
            raise TypeError(
                f"Invalid destination type: {type(destination)}. Expected Messageable or Interaction."
            )

        if not hasattr(self, "_author"):
            self._set_default_author(MISSING)
        if not hasattr(self, "_colour"):
            self._set_default_colour(MISSING)

        kwargs.pop("embed", None)
        kwargs["embeds"] = [self]
        return await send_method(content=content, **kwargs)  # type: ignore

    @property
    def colour(self) -> Optional[discord.Colour]:
        return getattr(self, "_colour", None)

    @colour.setter
    def colour(self, value: Optional[Union[int, discord.Colour]]) -> None:
        if not value or isinstance(value, discord.Colour):
            self._colour = value
        elif isinstance(value, int):
            self._colour = discord.Colour(value=value)
        else:
            raise TypeError(
                f"Expected discord.Colour, int, or None but received {value.__class__.__name__} instead."
            )

    color = colour

    @property
    def timestamp(self) -> Optional[datetime]:
        return getattr(self, "_timestamp", None)

    @timestamp.setter
    def timestamp(self, value: Optional[datetime]):
        if not value:
            self._timestamp = None
        elif isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.astimezone()
            self._timestamp = value
        else:
            raise TypeError(
                f"Expected datetime.datetime or None received {value.__class__.__name__} instead"
            )

    def __add_fields(
        self, fields: list[EmbedField], index: Optional[int] = None
    ) -> None:
        try:
            if index is not None:
                self._fields.insert(index, fields[0])
            else:
                self._fields.extend(fields)
        except AttributeError:
            self._fields = EmbedFields(self)
            if index is not None:
                self._fields.insert(index, fields[0])
            else:
                self._fields.extend(fields)

    @property
    def fields(self) -> EmbedFields:
        return getattr(self, "_fields", EmbedFields(self))  # type: ignore

    @fields.setter
    def fields(self, fields: Optional[list[EmbedField]]) -> None:
        self.clear_fields()
        if fields is None:
            return None

        if isinstance(fields, list):
            if not all(isinstance(field, EmbedField) for field in fields):
                raise TypeError(f"Expected all fields entries to be EmbedFields.")

            self.__add_fields(fields)
        else:
            raise TypeError(
                f"Expected list[EmbedField] or None received {fields.__class__.__name__} instead."
            )

    @property
    def image(self) -> EmbedMedia:
        return utils._maybe_construct("image", getattr(self, "_image", {}))

    @image.setter
    def image(self, url: str) -> None:
        self.set_image(url=str(url))

    @property
    def thumbnail(self) -> EmbedMedia:
        return utils._maybe_construct("thumbnail", getattr(self, "_thumbnail", {}))

    @thumbnail.setter
    def thumbnail(self, url: str) -> None:
        self.set_thumbnail(url=str(url))

    def medias(self) -> list[EmbedMedia]:
        media_attrs = ("_image", "_thumbnail", "_video", "_footer", "_author")
        medias = []
        for attr in media_attrs:
            if hasattr(self, attr):
                if attr in ("_footer", "_author"):
                    if _media := getattr(self, attr).media():
                        medias.append(_media)
                else:
                    medias.append(getattr(self, attr))

        return medias

    @property
    def footer(self) -> EmbedFooter:
        return utils._maybe_construct("footer", getattr(self, "_footer", {}))

    @footer.setter
    def footer(self, footer: Union[str, EmbedFooter]):
        if footer in (None, MISSING):
            del self._footer
            return

        if not isinstance(footer, (str, EmbedFooter)):
            raise ValueError(
                "footer must be a string or an instance of EmbedFooter, not {footer.__class__.__name__}"
            )

        if isinstance(footer, str):
            footer = EmbedFooter(text=footer)

        self._footer = footer.to_dict()

    @property
    def author(self) -> EmbedAuthor:
        return utils._maybe_construct("author", getattr(self, "_author", {}))

    @author.setter
    def author(self, author: EmbedAuthor) -> None:
        if author in (None, MISSING):
            del self._author
            return
        if not isinstance(author, EmbedAuthor):
            raise ValueError(
                f"author must be an instance of EmbedAuthor, not {author.__class__.__name__}"
            )

        self._author = author.to_dict()

    @property
    def video(self) -> EmbedMedia:
        return utils._maybe_construct("video", getattr(self, "_video", {}))

    @property
    def provider(self) -> EmbedProvider:
        return utils._maybe_construct("provider", getattr(self, "_provider", {}))

    def add_field(
        self, *, name: Any, value: Any, inline: bool = True, index: Optional[int] = None
    ) -> Self:
        field = EmbedField(name=name, value=value, inline=inline)
        self.append_field(field, index=index)

        return self

    def append_field(self, field: EmbedField, index: Optional[int] = None) -> Self:
        if not isinstance(field, EmbedField):
            raise TypeError("field must be an instance of EmbedField")

        if index:
            if not isinstance(index, int):
                raise TypeError("index must be an int")

            if index < 0:
                raise ValueError("index must be greater than 0")

        self.__add_fields([field], index)
        return self

    def add_fields(
        self,
        *namevalues: Field_Values,
        fields: Optional[list[EmbedField]] = None,
    ) -> Self:
        if fields:
            emfield: EmbedField
            for emfield in fields:
                self.append_field(emfield)

        elif namevalues:
            for values in namevalues:
                self.append_field(EmbedField.from_tuple(values))
        else:
            raise TypeError(
                "Expected the usage of either the fields kwarg or raw tuples."
            )

        return self

    def clear_fields(self) -> None:
        """Removes all fields from this embed."""
        try:
            del self._fields
        except AttributeError:
            pass

    def remove_field(self, index: int) -> None:
        try:
            del self._fields[index]
        except (AttributeError, IndexError):
            pass

    def edit_field(
        self,
        index: int,
        *,
        name: Optional[Any],
        value: Optional[Any],
        inline: Optional[bool] = None,
    ) -> Self:
        try:
            field = self._fields[index]
        except (TypeError, IndexError, AttributeError):
            raise IndexError("field index out of range")

        field.edit(name=name, value=value, inline=inline)
        return self

    def copy(self) -> Embed:
        return Embed.from_dict(self.to_dict())

    def clone(self) -> Self:
        del self._author_object
        copied = deepcopy(self)
        copied._author_object = self._author_object
        return copied

    def to_dict(self) -> EmbedData:
        result: dict[str, Any] = {}

        for key in self.__user_attributes__:
            if key[0] == "_" and hasattr(self, key):
                value = getattr(self, key)
                if key in ("_fields",):
                    value = value.to_dict()
                if is_dataclass(value):
                    value = value.to_dict()

                if key in ("_image", "_thumbnail"):
                    result[key[1:]] = value[key[1:]]
                else:
                    result[key[1:]] = value

        for attr in ("title", "description", "url", "type"):
            if value := result.get(attr):
                result[attr] = str(value)

        try:
            colour = result.pop("colour")
        except KeyError:
            pass
        else:
            if colour:
                result["color"] = colour.value

        try:
            timestamp = result.pop("timestamp")
        except KeyError:
            pass
        else:
            if timestamp:
                if timestamp.tzinfo:
                    final_timestamp = timestamp.astimezone(tz=timezone.utc)
                else:
                    final_timestamp = timestamp.replace(tzinfo=timezone.utc)

                result["timestamp"] = final_timestamp.isoformat()

        if self._check_limits:
            title = result.get("title", "")
            description = result.get("description", "")
            fields = result.get("fields", [])
            footer_text = result.get("footer", {}).get("text", "")
            author_name = result.get("author", {}).get("name", "")

            for key, value in (
                ("title", title),
                ("description", description),
                ("footer_text", footer_text),
                ("author_name", author_name),
                ("fields", fields),
            ):
                if len(value) > getattr(EMBED_LIMITS, key):
                    raise ValueError(
                        f"Embed {key} is too long. (Max: {getattr(EMBED_LIMITS, key)})"
                    )

        return result  # type: ignore

    @classmethod
    def from_dict(cls: Type[Self], data: EmbedData) -> Self:
        if isinstance(data, discord.Embed):
            return cls.from_dpy_embed(data)

        # we are bypassing __init__ here since it doesn't apply here
        self: Self = cls.__new__(cls)

        # fill in the basic fields
        self.type: EmbedTypeData = data.get("type")  # type: ignore

        self.title = data.get("title", None)

        self.description = data.get("description", None)
        self.url = data.get("url", None)

        if self.title is not None:
            self.title = str(self.title)

        if self.description is not None:
            self.description = str(self.description)

        if self.url is not None:
            self.url = str(self.url)

        try:
            self._colour = discord.Colour(value=data["color"])
        except KeyError:
            pass

        try:
            self._timestamp = discord.utils.parse_time(data["timestamp"])
        except KeyError:
            pass

        for attr in (
            "thumbnail",
            "provider",
            "author",
            "fields",
            "image",
            "footer",
            "video",
        ):
            try:
                data_value = data[attr]  # type: ignore
            except KeyError:
                continue
            else:
                if not is_dataclass(data_value):
                    data_cls = utils.attr_to_class[attr]  # type: ignore
                    # special case for fields
                    if data_cls is EmbedFields:
                        data_value: Sequence[EmbedFieldData]
                        data_cls: Type[EmbedFields]
                        data_value = data_cls.from_dict(self, data_value)
                    else:
                        if attr in ("image", "video", "thumbnail"):
                            data_value["media_type"] = EmbedMediaType[attr.upper()]

                        data_value = data_cls.from_dict(data_value)

                setattr(self, "_" + attr, data_value)

        return self

    @classmethod
    def from_dpy_embed(cls, embed_instance: discord.Embed) -> Self:
        if not isinstance(embed_instance, discord.Embed):
            raise TypeError("embed_instance must be an instance of discord.Embed")

        embed_dict: EmbedData = embed_instance.to_dict()
        return cls.from_dict(embed_dict)

    def cast(self) -> discord.Embed:
        return self  # type: ignore
