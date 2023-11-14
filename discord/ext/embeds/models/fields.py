from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Union, Optional, cast

from dataclasses import dataclass

from .base import BaseEmbedDataclass

if TYPE_CHECKING:
    from typing_extensions import Self

    from .._types import Field_Values, SupportsCastingToString

    from discord.types.embed import EmbedField as EmbedFieldData

__all__ = (
    "EmbedField",
    "EmbedFields",
)


@dataclass(eq=False)
class EmbedField(BaseEmbedDataclass):
    """Represents an embed field.

    Parameters
    ----------
    name: :class:`str`
        The name of the field.
    value: :class:`str`
        The value of the field.
    inline: :class:`bool`
        Whether the field is inline or not.
    index: Optional[:class:`int`]
        The index of the field.
    """

    name: SupportsCastingToString
    """The name of the field."""
    value: SupportsCastingToString
    """The value of the field."""
    inline: bool = True
    """Whether the field is inline or not."""
    index: Optional[int] = None
    """The index of the field."""

    def __post_init__(self) -> None:
        self.value = str(self.value) if self.value is not None else "\u200b"

    def fill_index(self, index: Optional[int], fields: list[EmbedField]) -> None:
        if index is None:
            inx = fields.index(self)
        inx = index
        self.index = inx

    @classmethod
    def from_tuple(cls, data: Field_Values) -> Self:
        if isinstance(data, dict):
            return cls.from_dict(cast("EmbedFieldData", data))

        def unpack_values(data: Union[tuple[int, bool], tuple[int], tuple[bool]]) -> tuple[bool, Optional[int]]:
            inline, index = False, None
            if len(data) == 2:
                if isinstance(data[0], bool):
                    inline, index = data
                else:
                    index, inline = data
            else:
                if isinstance(data[0], bool):
                    inline = data[0]
                else:
                    index = data[0]

            return inline, index  # type: ignore

        name, value, *others = data
        inline, index = unpack_values(others)  # type: ignore
        return cls(name, value, inline, index)

    def edit(
        self,
        *,
        name: Optional[SupportsCastingToString] = None,
        value: Optional[SupportsCastingToString] = None,
        inline: Optional[bool] = None,
        index: Optional[int] = None,
    ) -> Self:
        if name is not None:
            self.name = name
        if value is not None:
            self.value = value
        if inline is not None:
            self.inline = inline
        if index is not None:
            self.index = index

        return self


class EmbedFields(list[EmbedField]):
    def get(
        self,
        name: Optional[SupportsCastingToString] = None,
        value: Optional[SupportsCastingToString] = None,
        inline: Optional[bool] = None,
        index: Optional[int] = None,
    ) -> Optional[EmbedField]:
        for field in self:
            if name and field.name == name:
                return field
            if value and field.value == value:
                return field
            if inline is not None and field.inline == inline:
                return field
            if index is not None and field.index == index:
                return field

        return None

    def append(self, field: EmbedField, index: Optional[int] = None) -> None:
        index = index or field.index
        if index:
            self.insert(index, field)
        else:
            self.append(field)

        field.fill_index(index, self)

    def add(
        self,
        *,
        name: SupportsCastingToString,
        value: SupportsCastingToString,
        inline: bool = True,
        index: Optional[int] = None,
    ) -> None:
        field = EmbedField(name, value, inline, index)
        self.append(field, index)

    def to_dict(self) -> Sequence[EmbedFieldData]:
        return [field.to_dict for field in self.fields]  # type: ignore

    def add_from_dict(self, data: Sequence[EmbedFieldData]) -> None:
        self.extend(EmbedField.from_dict(field) for field in data)

    @classmethod
    def from_dict(cls, data: Sequence[EmbedFieldData]) -> Self:
        return cls(EmbedField.from_dict(field) for field in data)

    def __repr__(self) -> str:
        return f"<EmbedFields {len(self)} fields>"
