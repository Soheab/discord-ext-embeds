import datetime
import inspect
import reprlib
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Protocol

from discord.utils import MISSING

from .errors import LimitReached

if TYPE_CHECKING:

    class WithLen(Protocol):
        def __len__(
            self,
        ) -> int:
            ...


__all__ = ()


class _EmbedLimits:
    """Represents the limits of an embed.

    As documented in the API docs: https://discord.com/developers/docs/resources/channel#embed-object-embed-limits
    The limits are hardcoded and may have changed since the last update.
    Please open an issue if you think this is the case.

    These are all checked in :class:`Embed.to_dict` if ``check_limits`` is set to ``True``.

    Attributes
    ----------
    enabled: :class:`bool`
        Whether the limits should be checked or not.
    title: :class:`int`
        The maximum length of the title.
    description: :class:`int`
        The maximum length of the description.
    fields: :class:`int`
        The maximum amount of fields.
    field_name: :class:`int`
        The maximum length of the field name.
    field_value: :class:`int`
        The maximum length of the field value.
    footer_text: :class:`int`
        The maximum length of the footer text.
    author_name: :class:`int`
        The maximum length of the author name.
    embed: :class:`int`
        The maximum amount of characters in an embed.
    embeds: :class:`int`
        The maximum amount of embeds in a message.

        This is checked in :meth:`Embed.send` if ``check_limits`` is set to ``True``.
    last_updated: :class:`datetime.datetime`
        When the limits were last updated.
    """

    last_updated: ClassVar[datetime.date] = datetime.date(year=2023, month=11, day=23)
    __slots__ = (
        "title",
        "description",
        "fields",
        "field_name",
        "field_value",
        "footer_text",
        "author_name",
        "embed",
        "embeds",
        "_enabled",
    )

    def __init__(
        self,
        *,
        title: int,
        description: int,
        fields: int,
        field_name: int,
        field_value: int,
        footer_text: int,
        author_name: int,
        embed: int,
        embeds: int,
        enabled: bool = True,
    ) -> None:
        self._enabled: bool = enabled

        self.title: int = title
        self.description: int = description
        self.fields: int = fields
        self.field_name: int = field_name
        self.field_value: int = field_value
        self.footer_text: int = footer_text
        self.author_name: int = author_name
        self.embed: int = embed
        self.embeds: int = embeds

    @reprlib.recursive_repr()
    def __repr__(self) -> str:
        attrs = " ".join(f"{attr}={getattr(self, attr)!r}" for attr in self.__slots__)
        return f"<EmbedLimits {attrs}>"

    def __setattr__(self, name: str, value: Any, /) -> None:
        if name not in self.__slots__:
            raise TypeError(f"{name} is not a valid attribute.")
        if inspect.stack()[1].function not in ("__init__", "edit"):
            raise TypeError(f"{self.__class__.__name__} is immutable. Do .edit({name}={value!r}) instead.")
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer.")
        if value < 0:
            raise ValueError(f"{name} can't be negative.")

        super().__setattr__(name, value)

    def is_enabled(self) -> bool:
        """:class:`bool`: Whether the limits should be checked or not."""
        return self._enabled

    def edit(
        self,
        *,
        enabled: bool = MISSING,
        title: int = MISSING,
        description: int = MISSING,
        fields: int = MISSING,
        field_name: int = MISSING,
        field_value: int = MISSING,
        footer_text: int = MISSING,
        author_name: int = MISSING,
        embed: int = MISSING,
        embeds: int = MISSING,
    ) -> "_EmbedLimits":
        """Edits the limits.

        The API will error out if the limits are not valid.

        Parameters
        ----------
        enabled: :class:`bool`
            Whether the limits should be checked or not.
            This can be used to disable all limits at once.
        title: :class:`int`
            The maximum length of the title.
        description: :class:`int`
            The maximum length of the description.
        fields: :class:`int`
            The maximum amount of fields.
        field_name: :class:`int`
            The maximum length of the field name.
        field_value: :class:`int`
            The maximum length of the field value.
        footer_text: :class:`int`
            The maximum length of the footer text.
        author_name: :class:`int`
            The maximum length of the author name.
        embed: :class:`int`
            The maximum amount of characters in an embed.
        embeds: :class:`int`
            The maximum amount of embeds in a message.

            This is checked in :meth:`Embed.send`.
        """
        values = (
            (title, "title"),
            (description, "description"),
            (fields, "fields"),
            (field_name, "field_name"),
            (field_value, "field_value"),
            (footer_text, "footer_text"),
            (author_name, "author_name"),
            (embed, "embed"),
            (embeds, "embeds"),
            (enabled, "_enabled"),
        )
        for value, name in values:
            if value is MISSING:
                continue

            setattr(self, name, value)

        return self

    def check_limit_of(self, field: str, value: Optional["WithLen"], **extras: Any) -> None:
        """Checks if the value is within the limit of the field.

        Parameters
        ----------
        field: :class:`str`
            The name of the field to check.
        value: Optional[Any]
            The value of the field to check.

        Raises
        ------
        TypeError
            The field is not a valid field.
        LimitReached
            The value is too long.
        """
        if not self._enabled:
            return

        if not value:
            return

        if field not in self.__slots__:
            raise TypeError(f"{field} is not a valid field.")

        limit = getattr(self, field)
        if len(value) > limit:
            raise LimitReached(
                limit_of=field,
                limit=limit,
                current=len(value),
                object=extras.get("object"),
                field_index=extras.get("field_index"),
            )
