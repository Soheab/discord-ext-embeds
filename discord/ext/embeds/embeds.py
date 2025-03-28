from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Literal,
    Type,
    TypeVar,
    Union,
    Optional,
)

from copy import deepcopy
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
from .enums import EmbedMediaType, MultiImagesType
from . import utils, limit

if TYPE_CHECKING:
    from typing_extensions import Self

    from discord.types.embed import (
        Embed as EmbedData,
        EmbedType as EmbedTypeData,
    )

    from ._types import (
        PossibleMessage,
        SupportsCastingToString,
        PossibleClassTypes,
        Field_Values,
    )

    Interaction = discord.Interaction[Any]
    Context = commands.Context[Any]
    User = Union[discord.Member, discord.User]

__all__ = ("Embed",)


if TYPE_CHECKING:
    from typing_extensions import TypeVar  # noqa: F811 # it's different.

    TitleT = TypeVar("TitleT", bound=Optional["SupportsCastingToString"], default=None)
    DescriptionT = TypeVar("DescriptionT", bound=Optional["SupportsCastingToString"], default=None)
else:
    TitleT = TypeVar("TitleT", bound=Optional["SupportsCastingToString"], covariant=True)
    DescriptionT = TypeVar("DescriptionT", bound=Optional["SupportsCastingToString"], covariant=True)


class Embed(discord.Embed, Generic[TitleT, DescriptionT]):
    """A subclass of :class:`discord.Embed` that adds some extra functionality.

    Parameters
    ----------
    title: Optional[:class:`str`]
        The title of the embed.
    description: Optional[:class:`str`]
        The description of the embed.
    colour: Optional[Union[:class:`int`, :class:`discord.Colour`, :class:`str`]]
        The colour of the embed. Defaults to :attr:`discord.Colour.dark_theme`.
        If a string is passed, it's validated with :meth:`discord.Colour.from_str`.
    url: Optional[Any]
        The URL of the embed.
    timestamp: Optional[:class:`datetime.datetime`]
        The timestamp of the embed.
    image: Optional[Union[:class:`str`, :class:`discord.File`, :class:`EmbedMedia`]]
        The image of the embed. Can be a URL or a :class:`discord.File`.
    fields: Optional[list[:class:`EmbedField`]]
        The fields of the embed as a list of :class:`EmbedField`.
    thumbnail: Optional[Union[:class:`str`, :class:`discord.File`, :class:`EmbedMedia`]]
        The thumbnail of the embed. Can be a URL or a :class:`discord.File`.
    footer: Optional[Union[:class:`str`, :class:`EmbedFooter`, :class:`discord.Member`, :class:`discord.User`]]
        The footer of the embed. Can be a string for the text, an instance of :class:`EmbedFooter` or a user object.
        If a user object is passed, the footer text will be set to ``.display_name`` and icon_url to ``.display_avatar.url``.
    author: Optional[Union[:class:`str`, :class:`EmbedAuthor`, :class:`discord.Member`, :class:`discord.User`]]
        The author of the embed. Can be a string for the name, an instance of :class:`EmbedAuthor`  or a user object.
        If a user object is passed, the author name will be set to ``.display_name`` and icon_url to ``.display_avatar.url``.
    check_limits: :class:`bool`
        Whether to check the (hardcoded) embed limits as documented in the API docs. Defaults to ``True``.
        These limits can be edited by using ``.edit`` on the ``.limits`` attribute.
        Example:

        .. code-block:: python3
            :linenos:

            embed = Embed()
            # the API will error out if the limit is higher than they allow.
            embed.LIMITS.edit(
                title=100
            )

        :exc:`LimitReached` will be raised if the limit is reached.
    """

    # https://discord.com/developers/docs/resources/channel#embed-object
    LIMITS: limit._EmbedLimits = limit._EmbedLimits(
        title=256,
        description=4096,
        fields=25,
        field_name=256,
        field_value=1024,
        footer_text=2048,
        author_name=256,
        embed=6000,
        embeds=10,
    )

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
        "_fields",
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
        "_flags",
        "_check_limits",
    )

    def __init__(
        self,
        *,
        title: TitleT = None,
        description: DescriptionT = None,
        colour: Optional[Union[int, discord.Colour, SupportsCastingToString]] = discord.Colour.dark_theme(),
        color: Optional[Union[int, discord.Colour, SupportsCastingToString]] = discord.Colour.dark_theme(),
        url: Optional[SupportsCastingToString] = None,
        timestamp: Optional[datetime] = None,
        image: Optional[Union[SupportsCastingToString, discord.File, EmbedMedia]] = None,
        fields: list[EmbedField] = [],
        thumbnail: Optional[Union[SupportsCastingToString, discord.File, EmbedMedia]] = None,
        footer: Optional[Union[SupportsCastingToString, EmbedFooter, User]] = None,
        author: Optional[Union[SupportsCastingToString, EmbedAuthor, User]] = None,
        check_limits: bool = True,
    ) -> None:
        self._check_limits = self.LIMITS.is_enabled() if check_limits else False

        self.type: EmbedTypeData = "rich"
        self._flags: int = 0

        with_set_methods = (
            ("title", title),
            ("description", description),
            ("url", url),
            ("timestamp", timestamp),
        )
        for attr, value in with_set_methods:
            getattr(self, f"set_{attr}")(value)

        _colour = colour if colour is not None else color
        if _colour is not None:
            self.colour = _colour

        if fields:
            self.fields = fields

        if image is not None:
            self.image = image

        if thumbnail is not None:
            self.thumbnail = thumbnail

        if footer is not None:
            self.footer = footer

        if author is not None:
            self.author = author

    def __str__(self) -> str:
        return self.title or ""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(title={self.title!r} color={self.color!r} url={self.url!r} timestamp={self.timestamp!r})"

    def __len__(self) -> int:
        count: int = 0
        if self.title:
            count += len(self.title)
        if self.description:
            count += len(self.description)
        if self.footer:
            count += len(self.footer)
        if self.author:
            count += len(self.author)
        if self.fields:
            count += self.fields.total_fields_length()

        return count

    def __bool__(self) -> bool:
        return any(
            (
                self.title,
                self.description,
                self.url,
                self.colour,
                self.timestamp,
                self.footer,
                self.author,
                self.fields,
                self.image,
                self.thumbnail,
                self.video,
                self.provider,
            )
        )

    def _delete_attribute(self, attribute: str) -> None:
        try:
            delattr(self, attribute)
        except AttributeError:
            pass

    @classmethod
    def from_dpy_embed(cls, embed_instance: discord.Embed) -> Embed[Any, Any]:
        """Converts a :class:`discord.Embed` to this class.

        Parameters
        ----------
        embed_instance: :class:`discord.Embed`
            The embed instance to convert.

        Returns
        -------
        :class:`Embed`
            The converted embed.
        """
        if not isinstance(embed_instance, discord.Embed):
            raise TypeError("embed_instance must be an instance of discord.Embed")

        embed_dict: EmbedData = embed_instance.to_dict()
        return cls.from_dict(embed_dict)

    @classmethod
    def with_multiple_images(
        cls,
        *images: Union[SupportsCastingToString, discord.File, EmbedMedia],
        type: Union[MultiImagesType, Literal["image", "thumbnail"]] = MultiImagesType.image,
        title: Optional[SupportsCastingToString] = None,
        description: Optional[SupportsCastingToString] = None,
        colour: Optional[Union[int, discord.Colour, str]] = discord.Colour.dark_theme(),
        color: Optional[Union[int, discord.Colour, str]] = discord.Colour.dark_theme(),
        url: Optional[SupportsCastingToString] = None,
        timestamp: Optional[datetime] = None,
        fields: list[EmbedField] = [],
        footer: Optional[Union[SupportsCastingToString, EmbedFooter, User]] = None,
        author: Optional[Union[SupportsCastingToString, EmbedAuthor, User]] = None,
        check_limits: bool = True,
    ) -> list[Embed[Any, Any]]:
        """Helper method to create an embed with multiple images.

        This will create a main embed with the passed parameters and then create an embed for each image passed.
        This is currenly a "hack" as it's not documented in the API docs.
        At the time of writing, the `url` field is required for this to work.

        Currently only 4 first images are shown, the rest are ignored (by the api).

        Parameters
        ----------
        type: :class:`MultiImagesType`
            The type of the images. Can be ``image`` or ``thumbnail``. Defaults to ``image``.
        *images: Union[:class:`str`, :class:`discord.File`, :class:`EmbedMedia`]
            The images to add to the embed. Can be a URL, a :class:`discord.File` or an instance of :class:`EmbedMedia`.

        Other parameters are the same as :class:`Embed`. They are used for the main, first embed.

        Returns
        -------
        list[:class:`Embed`]
            A list of :class:`Embed` each representing an embed with an image.
            This can be passed to the `embeds=` kwarg of all the send methods.
        """
        to_call = "set_image" if type is MultiImagesType.image else "set_thumbnail"
        _images = list(images)

        main_embed = cls.__new__(cls)
        main_embed.__init__(
            title=title,
            description=description,
            colour=colour,
            color=color,
            url=url,
            timestamp=timestamp,
            fields=fields,
            footer=footer,
            author=author,
            check_limits=check_limits,
        )
        first_image = _images.pop(0)
        getattr(main_embed, to_call)(first_image)

        embeds: list[Embed[Any, Any]] = [main_embed]

        image_type = type
        if not isinstance(image_type, MultiImagesType):
            try:
                image_type = MultiImagesType(type)
            except ValueError:
                raise ValueError(
                    "type must be an instance of MultiImagesType or one of 'image', 'thumbnail'. Got {type!r} instead."
                )

        for image in _images:
            embed: Embed[Any, Any] = main_embed.clone()
            getattr(embed, to_call)(image)
            embeds.append(embed)

        return embeds

    def medias(self) -> list[EmbedMedia]:
        """Returns a list of all medias in the embed.

        This includes the image, thumbnail, video, footer icon and author icon.
        :attr:`EmbedMedia.media_type` can be used to check the type of media.

        Returns
        -------
        list[:class:`EmbedMedia`]
            A list of :class:`EmbedMedia` each representing a media in the embed.
        """
        media_attrs = ("_image", "_thumbnail", "_video", "_footer", "_author")
        medias: list[EmbedMedia] = []
        for attr in media_attrs:
            try:
                attr_value = getattr(self, attr)
            except AttributeError:
                continue
            else:
                if attr in ("_footer", "_author"):
                    if _media := attr_value.media:
                        medias.append(_media)
                else:
                    medias.append(attr_value)

        return medias

    def files(self) -> list[discord.File]:
        """Returns a list of all files in the embed.

        This includes the image, thumbnail, video, footer icon and author icon.

        Returns
        -------
        list[:class:`discord.File`]
            A list of :class:`discord.File` each representing a file in the embed.
        """
        files: list[discord.File] = []
        for media in self.medias():
            if media.file:
                files.append(media.file)

        return files

    # BASIC ATTRIBUTES

    def set_description(self, description: Optional[SupportsCastingToString], /) -> Self:
        """Sets the description of the embed.

        Parameters
        ----------
        description: Optional[:class:`str`]
            The description of the embed. ``None`` to remove.

        Returns
        -------
        :class:`Embed`
            The embed itself.
        """
        self.description = str(description) if description is not None else None
        return self

    def set_title(self, title: Optional[SupportsCastingToString], /) -> Self:
        """Sets the title of the embed.

        Parameters
        ----------
        title: Optional[:class:`str`]
            The title of the embed. ``None`` to remove.

        Returns
        -------
        :class:`Embed`
            The embed itself.
        """
        self.title = str(title) if title is not None else None
        return self

    def set_url(self, url: Optional[SupportsCastingToString], /) -> Self:
        """Sets the URL of the embed.

        Parameters
        ----------
        url: Optional[:class:`str`]
            The URL of the embed. ``None`` to remove.

        Returns
        -------
        :class:`Embed`
            The embed itself.
        """
        self.url = str(url) if url is not None else None
        return self

    def set_colour(self, colour: Optional[Union[int, discord.Colour]], /) -> Self:
        """Sets the colour of the embed.

        Parameters
        ----------
        colour: Optional[Union[:class:`int`, :class:`discord.Colour`]]
            The colour of the embed. ``None`` to remove the colour.

        Returns
        -------
        :class:`Embed`
            The embed itself.
        """
        self.colour = colour
        return self

    set_color = set_colour
    """Alias for :meth:`Embed.set_colour`."""

    def set_timestamp(self, timestamp: Optional[datetime], /) -> Self:
        """Sets the timestamp of the embed.

        Parameters
        ----------
        timestamp: Optional[:class:`datetime.datetime`]
            The timestamp of the embed.

        Returns
        -------
        :class:`Embed`
            The embed itself.
        """
        self.timestamp = timestamp
        return self

    def set_image(
        self,
        image: Optional[Union[SupportsCastingToString, discord.File, EmbedMedia]] = None,
        *,
        url: Optional[SupportsCastingToString] = None,
    ) -> Self:
        """Sets the image of the embed.

        Parameters
        ----------
        image: Optional[Union[:class:`str`, :class:`discord.File`]]
            The image of the embed. Can be a URL or a :class:`discord.File`. ``None`` to remove the image.
        url: Optional[:class:`str`]
            The URL of the image. ``None`` to remove the image.
            This is for backwards compatibility. If ``image`` is passed, this is ignored.

        Raises
        ------
        ValueError
            Must pass either image or url. If both are passed, ValueError is raised.
        """
        if not (url or image):
            self._delete_attribute("_image")
            return self

        self._image = EmbedMedia.construct(EmbedMediaType.image, image or url)  # type: ignore
        return self

    def set_thumbnail(
        self,
        thumbnail: Optional[Union[SupportsCastingToString, discord.File, EmbedMedia]] = None,
        *,
        url: Optional[SupportsCastingToString] = None,
    ) -> Self:
        """Sets the thumbnail of the embed.

        Parameters
        ----------
        thumbnail: Optional[Union[:class:`str`, :class:`discord.File`, :class:`EmbedMedia`]]
            The thumbnail of the embed. Can be a URL, a :class:`discord.File` or :class:`EmbedMedia` object. ``None`` to remove the thumbnail.
        url: Optional[:class:`str`]
            The URL of the thumbnail. ``None`` to remove the thumbnail.
            This is for backwards compatibility. If ``thumbnail`` is passed, this is ignored.

        Raises
        ------
        ValueError
            Must pass either image or url. If both are passed, ValueError is raised.
        """
        if not (url or thumbnail):
            self._delete_attribute("_thumbnail")
            return self

        self._image = EmbedMedia.construct(EmbedMediaType.thumbnail, thumbnail or url)  # type: ignore
        return self

    def set_footer(
        self,
        *,
        text: Optional[SupportsCastingToString],
        icon: Optional[Union[SupportsCastingToString, discord.File]] = None,
        icon_url: Optional[SupportsCastingToString] = None,
    ) -> Self:
        """Sets the footer of the embed.

        Parameters
        ----------
        text: :class:`str`
            The text of the footer. ``None`` to remove the footer.
        icon: Optional[Union[:class:`str`, :class:`discord.File`]]
            The icon of the footer. Can be a URL or a :class:`discord.File`.
        icon_url: Optional[:class:`str`]
            The URL of the footer icon.
            This is for backwards compatibility. If ``icon`` is passed, this is ignored.

        Returns
        -------
        :class:`Embed`
            The embed itself.
        """
        if not text:
            self._delete_attribute("_footer")
            return self

        kwargs: dict[str, Any] = {"text": text}
        if icon is not None:
            if isinstance(icon, discord.File):
                kwargs["icon_file"] = icon
            else:
                kwargs["icon_url"] = icon
        else:
            kwargs["icon_url"] = icon_url

        self._footer = EmbedFooter(**kwargs)
        return self

    def set_author(
        self,
        *,
        name: Optional[SupportsCastingToString],
        icon: Optional[Union[SupportsCastingToString, discord.File]] = None,
        icon_url: Optional[SupportsCastingToString] = None,
    ) -> Self:
        """Sets the footer of the embed.

        Parameters
        ----------
        name: :class:`str`
            The name of the author. ``None`` to remove the author.
        icon: Optional[Union[:class:`str`, :class:`discord.File`]]
            The icon of the author. Can be a URL or a :class:`discord.File`.
        icon_url: Optional[:class:`str`]
            The URL of the author icon.
            This is for backwards compatibility. If ``icon`` is passed, this is ignored.

        Returns
        -------
        :class:`Embed`
            The embed itself.
        """
        if not name:
            self._delete_attribute("_author")
            return self

        kwargs: dict[str, Any] = {"name": name}
        if icon is not None:
            if isinstance(icon, discord.File):
                kwargs["icon_file"] = icon
            else:
                kwargs["icon_url"] = icon
        else:
            kwargs["icon_url"] = icon_url

        self._author = EmbedAuthor(**kwargs)
        return self

    async def send(
        self,
        destination: Union[Messageable, Interaction],
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[PossibleMessage]:
        """Sends the embed to a destination.

        This will convert the `embed` kwarg to `embeds` and append this embed to it. Same for `file` and `files`.

        You are not required to use this method to send the embed. You can use the destination's send method directly.
        Don't forget to send the files with the embed if you have any, you can get them with :meth:`Embed.files`.

        Parameters
        ----------
        destination: Union[:class:`Messageable`, :class:`Interaction`]
            The destination to send the embed to. This can be a :class:`discord.Messageable` or a :class:`discord.Interaction`.
        content: Optional[:class:`str`]
            The content to send with the embed.
        **kwargs: Any
            Additional keyword arguments to pass to the destination's send method.

        Raises
        ------
        TypeError
            Invalid destination type passed.
        """
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
            raise TypeError(f"Invalid destination type: {type(destination)}. Expected Messageable or Interaction.")

        embeds = kwargs.pop("embeds", [])
        embeds.append(self)
        if "embed" in kwargs:
            embeds.append(kwargs.pop("embed"))

        files = kwargs.pop("files", [])
        files.extend(self.files())
        if "file" in kwargs:
            files.append(kwargs.pop("file"))

        kwargs["embeds"] = embeds
        kwargs["files"] = files
        self.LIMITS.check_limit_of("embeds", embeds)
        return await send_method(content=content, **kwargs)  # type: ignore

    # COLOUR

    @property
    def colour(self) -> Optional[discord.Colour]:
        """The colour of the embed."""
        return getattr(self, "_colour", None)

    @colour.setter
    def colour(self, value: Optional[Union[int, discord.Colour, SupportsCastingToString]]) -> None:
        """Sets the colour of the embed.

        Parameters
        ----------
        value: Optional[Union[:class:`int`, :class:`discord.Colour`, :class:`str`]]
            The colour of the embed. ``None`` to remove the colour.
            If a string is passed, it's validated with :meth:`discord.Colour.from_str`.

        Raises
        -------
        ValueError
            The string could not be converted into a colour.
        TypeError
            ``value`` is not an instance of :class:`discord.Colour`, int, str or None.
        """
        self._colour = utils.handle_colour({"colour": value})

    @colour.deleter
    def colour(self) -> None:
        """Removes the colour from the embed."""
        self._delete_attribute("_colour")

    color = colour

    # FIELDS MANAGEMENT

    def clear_fields(self) -> None:
        """Removes all fields from the embed."""
        self._delete_attribute("_fields")

    def __add_fields(self, fields: list[EmbedField], index: Optional[int] = None) -> None:
        if not fields:
            return None

        try:
            if index is not None:
                self._fields.insert(index, fields[0])
            else:
                self._fields.extend(fields)
        except AttributeError:
            self._fields = EmbedFields()
            if index is not None:
                self._fields.insert(index, fields[0])
            else:
                self._fields.extend(fields)

    @property
    def fields(self) -> EmbedFields:
        """The fields of the embed.

        Returns
        -------
        :class:`EmbedFields`
            An instance of :class:`EmbedFields` that contains the fields of the embed.
            You can loop over this object to get the fields or use the methods to get, add, edit or remove fields.
        """
        return getattr(self, "_fields", EmbedFields())  # type: ignore

    @fields.setter
    def fields(self, fields: Optional[list[EmbedField]]) -> None:
        """Sets the fields of the embed.

        This will overwrite all current fields.

        Parameters
        ----------
        fields: Optional[list[:class:`EmbedField`]]
            The fields to set. ``None`` or an empty list to remove all fields.
        """
        self.clear_fields()
        if fields is None:
            self._delete_attribute("_fields")
            return None

        if isinstance(fields, list):
            if not all(isinstance(field, EmbedField) for field in fields):
                raise TypeError("Expected all fields entries to be EmbedFields.")

            self.__add_fields(fields)
        else:
            raise TypeError(f"Expected list[EmbedField] or None received {fields.__class__.__name__} instead.")

    @fields.deleter
    def fields(self) -> None:
        """Removes all fields from the embed."""
        self._delete_attribute("_fields")

    def add_field(
        self,
        *,
        name: SupportsCastingToString,
        value: SupportsCastingToString,
        inline: bool = True,
        index: Optional[int] = None,
    ) -> Self:
        """Adds a field to the embed.

        Parameters
        ----------
        name: :class:`str`
            The name of the field.
        value: :class:`str`
            The value of the field.
        inline: :class:`bool`
            Whether the field should be inline or not. Defaults to ``True``.
        index: Optional[:class:`int`]
            The position to insert the field at. Defaults to ``None`` which will let discord decide the position.
            Be aware that the position passed here is not guaranteed be the final position of the field on the client.

        Raises
        ------
        ValueError
            ``index`` must be greater than 0.
        TypeError
            ``index`` must be an int.

        Returns
        -------
        :class:`Embed`
            The embed itself.
        """
        embed_field = EmbedField(name=name, value=value, inline=inline)
        self.append_field(embed_field, index=index)

        return self

    def append_field(self, field: EmbedField, index: Optional[int] = None) -> Self:
        """Appends a field to the embed.

        Parameters
        ----------
        field: :class:`EmbedField`
            The field to append.
        index: Optional[:class:`int`]
            The position to insert the field at. Defaults to ``None`` which will let discord decide the position.
            Be aware that the position passed here is not guaranteed be the final position of the field on the client.

        Raises
        ------
        ValueError
            ``index`` must be greater than 0.
        TypeError
            ``index`` must be an int or ``field`` is not an instance of :class:`EmbedField`.

        Returns
        -------
        :class:`Embed`
            The embed itself.
        """
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
        """Adds multiple fields to the embed.

        Parameters
        ----------

        *namevalues: Union[tuple[:class:`str`, :class:`str`], tuple[:class:`str`, :class:`str`, :class:`bool`], tuple[:class:`str`, :class:`str`, :class:`bool`, :class:`int`], tuple[:class:`str`, :class:`str`, :class:`int`], dict[:class:`str`, Any]]
            The fields to add. Can be a tuple of ``(name, value)`` or ``(name, value, inline)`` or ``(name, value, inline, index)`` or a dict: ``{"name": name, "value": value}``or ``{"name": name, "value": value, "inline": inline}`` or ``{"name": name, "value": value, "inline": inline, "index": index}``.
            Additional values are ignored.
            ``index`` is the position to insert the field at. Defaults to ``None`` which will let discord decide the position.
            Be aware that the position passed here is not guaranteed be the final position of the field on the client.

        fields: Optional[list[:class:`EmbedField`]]
            A list of :class:`EmbedField` to add.

        Example
        --------
        .. code-block:: python3
            :linenos:

            embed = Embed()
            embed.add_fields(
                ("Field 1", "Value 1"),
                ("Field 2", "Value 2", True),
                ("Field 3", "Value 3", False, 2),
                ("Field 4", "Value 4", 2),
                {"name": "Field 5", "value": "Value 5"},
                fields=[EmbedField(name="Field 6", value="Value 6")]
            )
            embed.add_fields(
                ("Field 7", "Value 7", False, 7),
                {"name": "Field 8", "value": "Value 8", "inline": True},
                {"name": "Field 8", "value": "Value 8", "index": 5},
                fields=[
                    EmbedField(name="Field 5", value="Value 5"),
                    EmbedField(name="Field 6", value="Value 6", inline=True),
                    EmbedField(name="Field 7", value="Value 7", inline=False, index=2),
                    EmbedField(name="Field 8", value="Value 8", index=2),
                ]
            )

        Raises
        ------
        TypeError
            Invalid type passed or ``fields`` is not a list of :class:`EmbedField`.
        ValueError
            ``index`` must be greater than 0.

        Returns
        -------
        :class:`Embed`
            The embed itself.
        """
        if fields:
            if not isinstance(fields, list):
                raise TypeError("fields must be a list of EmbedField")

            if not all(isinstance(field, EmbedField) for field in fields):
                raise TypeError("Expected all fields entries to be an instance of EmbedField.")

            emfield: EmbedField
            for emfield in fields:
                self.append_field(emfield)

        elif namevalues:
            for values in namevalues:
                self.append_field(EmbedField.from_tuple(values))
        else:
            raise TypeError("Expected the usage of either the fields kwarg or raw tuples.")

        return self

    def remove_field(self, index: int) -> None:
        """Removes a field from the embed.

        Parameters
        ----------
        index: :class:`int`
            The index of the field to remove.
        """
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
    ) -> EmbedField:
        """Edits a field in the embed.

        Parameters
        ----------
        index: :class:`int`
            The index of the field to edit.
        name: Optional[:class:`str`]
            The new name of the field. Defaults to ``None`` which will not change the name.
        value: Optional[:class:`str`]
            The new value of the field. Defaults to ``None`` which will not change the value.
        inline: Optional[:class:`bool`]
            The new inline value of the field. Defaults to ``None`` which will not change the inline value.

        Raises
        ------
        IndexError
            Field index out of range.

        Returns
        -------
        :class:`EmbedField`
            The edited field.
        """
        try:
            field = self._fields[index]
        except (TypeError, IndexError, AttributeError):
            raise IndexError("field index out of range")

        field.edit(name=name, value=value, inline=inline)
        return field

    # ------------------

    # IMAGE

    @property
    def image(self) -> EmbedMedia:
        """The image of the embed.

        Returns
        -------
        :class:`EmbedMedia`
            An instance of :class:`EmbedMedia` that contains the image of the embed.
            Use ``.url`` to get the URL of the image.
        """
        return utils._maybe_construct("image", getattr(self, "_image", {}))

    @image.setter
    def image(
        self,
        value: Optional[Union[SupportsCastingToString, discord.File, EmbedMedia]],
    ) -> None:
        """Sets the image of the embed.

        Parameters
        ----------
        value: Union[:class:`str`, :class:`discord.File`, :class:`EmbedMedia`]
            The URL or file of the image. Can be a URL, a :class:`discord.File` or an instance of :class:`EmbedMedia`.
            ``None`` to remove the image.
        """
        if not value:
            self._delete_attribute("_image")
            return

        self.set_image(image=value)

    @image.deleter
    def image(self) -> None:
        """Removes the image of the embed."""
        self._delete_attribute("_image")

    # ------------------

    # THUMBNAIL

    @property
    def thumbnail(self) -> EmbedMedia:
        """The thumbnail of the embed.

        Returns
        -------
        :class:`EmbedMedia`
            An instance of :class:`EmbedMedia` that contains the thumbnail of the embed.
            Use ``.url`` to get the URL of the thumbnail.
        """
        return utils._maybe_construct("thumbnail", getattr(self, "_thumbnail", {}))

    @thumbnail.setter
    def thumbnail(
        self,
        value: Optional[Union[SupportsCastingToString, discord.File, EmbedMedia]],
    ) -> None:
        """Sets the image of the embed.

        Parameters
        ----------
        value: Union[:class:`str`, :class:`discord.File`, :class:`EmbedMedia`]
            The URL or file of the thumbnail. Can be a URL, a :class:`discord.File` or an instance of :class:`EmbedMedia`.
            ``None`` to remove the thumbnail.
        """
        if not value:
            self._delete_attribute("_thumbnail")
            return

        self.set_thumbnail(thumbnail=value)

    @thumbnail.deleter
    def thumbnail(self) -> None:
        """Removes the thumbnail of the embed."""
        self._delete_attribute("_thumbnail")

    # ------------------

    # FOOTER

    @property
    def footer(self) -> EmbedFooter:
        """The footer of the embed.

        Returns
        -------
        :class:`EmbedFooter`
            An instance of :class:`EmbedFooter` representing the footer of the embed.
            Use ``.text`` to get the text of the footer, if applicable.
        """
        return utils._maybe_construct("footer", getattr(self, "_footer", {}))

    @footer.setter
    def footer(self, footer: Union[SupportsCastingToString, EmbedFooter, User]) -> None:
        """Sets the footer of the embed.

        Parameters
        ----------
        footer: Union[:class:`str`, :class:`EmbedFooter`, :class:`discord.Member`, :class:`discord.User`]
            The footer of the embed. Can be a string for the text, an instance of :class:`EmbedFooter` or a user object.
            ``None`` to remove the footer.
            If a user object is passed, the footer text will be set to ``.display_name`` and icon_url to ``.display_avatar.url``.

        Raises
        ------
        TypeError
            Invalid footer type passed.
        """
        if footer in (None, discord.utils.MISSING):
            del self._footer
            return

        if not isinstance(footer, (str, EmbedFooter, discord.User, discord.Member)):
            raise TypeError(
                f"footer must be a string, an instance of EmbedFooter or a discord.User/Member object, not {footer!r}"
            )

        if isinstance(footer, (discord.User, discord.Member)):
            footer = EmbedFooter(text=footer.display_name, icon_url=footer.display_avatar.url)
        elif not isinstance(footer, EmbedFooter):
            footer = EmbedFooter(text=footer)

        self._footer = footer

    @footer.deleter
    def footer(self) -> None:
        """Removes the footer of the embed."""
        self._delete_attribute("_footer")

    # ------------------

    # AUTHOR

    @property
    def author(self) -> EmbedAuthor:
        """The author of the embed.

        Returns
        -------
        :class:`EmbedAuthor`
            An instance of :class:`EmbedAuthor` representing the author of the embed.
            Use ``.name`` to get the name of the author, if applicable.
        """
        return utils._maybe_construct("author", getattr(self, "_author", {}))

    @author.setter
    def author(self, author: Union[SupportsCastingToString, EmbedAuthor, User]) -> None:
        """Sets the author of the embed.

        Parameters
        ----------
        author: Union[:class:`str`, :class:`EmbedAuthor`, :class:`discord.Member`, :class:`discord.User`]
            The author of the embed. Can be a string for the name, an instance of :class:`EmbedAuthor` or a user object.
            ``None`` to remove the author.
            If a user object is passed, the author name will be set to ``.display_name`` and icon_url to ``.display_avatar.url``.

        Raises
        ------
        TypeError
            Invalid author type passed.
        """
        if author in (None, discord.utils.MISSING):
            try:
                del self._author
            except AttributeError:
                pass
            return

        if not isinstance(author, (str, EmbedAuthor, discord.User, discord.Member)):
            raise TypeError(
                f"author must be a string, an instance of EmbedAuthor or a discord.User/Member object, not {author!r}"
            )

        if isinstance(author, (discord.User, discord.Member)):
            author = EmbedAuthor(name=author.display_name, icon_url=author.display_avatar.url)
        elif not isinstance(author, EmbedAuthor):
            author = EmbedAuthor(name=author)

        self._author = author

    @author.deleter
    def author(self) -> None:
        """Removes the author of the embed."""
        self._delete_attribute("_author")

    # ------------------

    # VIDEO

    @property
    def video(self) -> EmbedMedia:
        """The video of the embed.

        Bots cannot send videos in embeds.

        Returns
        -------
        :class:`EmbedMedia`
            An instance of :class:`EmbedMedia` representing the video of the embed.
            Use ``.url`` to get the URL of the video, if applicable.
        """
        return utils._maybe_construct("video", getattr(self, "_video", {}))

    # ------------------

    # PROVIDER

    @property
    def provider(self) -> EmbedProvider:
        """The provider of the embed.

        This is only used for links posted by third parties.

        Returns
        -------
        :class:`EmbedProvider`
            An instance of :class:`EmbedProvider` representing the provider of the embed.
            Use ``.name`` to get the name of the provider, if applicable.
        """
        return utils._maybe_construct("provider", getattr(self, "_provider", {}))

    # ------------------
    # FLAGS

    @property
    def flags(self) -> discord.EmbedFlags:
        """:class:`EmbedFlags`: The flags of this embed.

        .. versionadded:: 2.5
        """
        return discord.EmbedFlags._from_value(self._flags or 0)

    # ------------------

    # COPY / CLONE

    def copy(self) -> Embed[Any, Any]:
        """:class:`Embed`: Returns a copy of the embed."""
        return self.__class__.from_dict(self.to_dict())

    def clone(self) -> Embed[Any, Any]:
        """Returns a clone of the embed.

        This will copy the embed and set the author object to the current author object.

        Returns
        -------
        :class:`Embed`
            The cloned embed.
        """
        # User/Member objects are not deepcopyable
        author = self.author
        footer = self.footer
        del self.author
        del self.footer
        copied = deepcopy(self)
        if isinstance(author, EmbedAuthor):
            copied.author = author
        if isinstance(footer, EmbedFooter):
            copied.footer = footer
        return copied

    # ------------------

    # TO/FROM DICT

    def to_dict(self) -> EmbedData:
        """Returns a dict representation of the embed."""
        result: dict[str, Any] = {}

        for key in self.__user_attributes__:
            if key[0] == "_" and hasattr(self, key):
                value = getattr(self, key)
                if not value:
                    continue
                if key in ("_fields",):
                    value = value.to_dict()
                if is_dataclass(value):
                    value = value.to_dict()  # type: ignore # dwai

                if key in ("_image", "_thumbnail"):
                    try:
                        result[key[1:]] = value[key[1:]]
                    except KeyError:
                        continue
                else:
                    result[key[1:]] = value

        for attr in ("title", "description", "url", "type"):
            if value := getattr(self, attr, None):
                result[attr] = str(value)

        result["flags"] = self._flags

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
            limits = self.LIMITS

            # embed
            limits.check_limit_of("embed", self)

            # title
            limits.check_limit_of("title", self.title)
            # description
            limits.check_limit_of("description", self.description)
            # footer_text
            limits.check_limit_of("footer_text", self.footer.text)
            # author_name
            limits.check_limit_of("author_name", self.author.name)
            # fields
            if self.fields:
                # fields
                limits.check_limit_of("fields", self.fields)
                for idx, field in enumerate(self.fields):
                    # field_name
                    limits.check_limit_of("field_name", field.name, field_index=idx, object=field)
                    # field_value
                    limits.check_limit_of("field_value", field.value, field_index=idx, object=field)

        return result  # type: ignore

    @classmethod
    def from_dict(cls: Type[Self], data: EmbedData) -> Embed[Any, Any]:
        """Constucts this class from a dict.

        Parameters
        ----------
        data: dict[Any, Any]
            The dict to construct the embed from.

        Returns
        -------
        :class:`Embed`
            The constructed embed.
        """
        # we are bypassing __init__ here since it doesn't apply here
        self: Self = cls.__new__(cls)
        # set in __init__ but we are bypassing it
        self._check_limits = True

        # fill in the basic fields
        self.type: EmbedTypeData = data.get("type")  # type: ignore
        self._flags = data.get("flags", 0)

        self.title = data.get("title", None)

        self.description = data.get("description", None)
        self.url = data.get("url", None)

        if self.title is not None:
            self.title = str(self.title)

        if self.description is not None:
            self.description = str(self.description)

        if self.url is not None:
            self.url = str(self.url)

        if (colour := utils.handle_colour(data)) is not None:  # type: ignore
            self._colour = colour

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
                data_value = data[attr]
            except KeyError:
                continue
            else:
                if not is_dataclass(data_value):
                    data_cls = attr_to_class[attr]
                    if attr in ("image", "video", "thumbnail"):
                        data_value["media_type"] = EmbedMediaType[attr.lower()]  # type: ignore # if-statement above ensures this is valid

                        data_value = data_cls.from_dict(data_value)  # type: ignore # dwai

                setattr(self, "_" + attr, data_value)

        return self

    # ------------------


attr_to_class: dict[str, PossibleClassTypes] = {
    "footer": EmbedFooter,
    "fields": EmbedFields,
    "author": EmbedAuthor,
    "provider": EmbedProvider,
    "image": EmbedMedia,
    "thumbnail": EmbedMedia,
    "video": EmbedMedia,
}
