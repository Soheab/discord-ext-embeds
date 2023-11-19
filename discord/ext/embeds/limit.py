from datetime import datetime
from typing import ClassVar, NamedTuple

from discord.utils import MISSING

__all__ = ()
class _EmbedLimits(NamedTuple):
    last_updated: ClassVar[datetime] = datetime(year=2023, month=11, day=15)

    title: int
    description: int
    fields: int
    field_name: int
    field_value: int
    footer_text: int
    author_name: int

    def get_limit_of(self, name: str) -> int:
        aliases = {
            "author": "author_name",
            "footer": "footer_text",
            "field": "fields",
        }
        name = aliases.get(name, name)
        try:
            return getattr(self, name)
        except AttributeError:
            valid_attrs = ", ".join(k for k, v in self.__annotations__.items() if v is int)
            raise ValueError(f"{name} is not a valid embed attribute. Valid attributes are: {valid_attrs}")

    def edit(
        self,
        *,
        title: int = MISSING,
        description: int = MISSING,
        fields: int = MISSING,
        field_name: int = MISSING,
        field_value: int = MISSING,
        footer_text: int = MISSING,
        author_name: int = MISSING,
    ) -> "_EmbedLimits":
        kwargs = {}
        values = ((title, "title"), (description, "description"), (fields, "fields"), (field_name, "field_name"), (field_value, "field_value"), (footer_text, "footer_text"), (author_name, "author_name"))	
        for value, name in values:
            if value is MISSING:
                continue
            if not isinstance(value, int):
                raise TypeError(f"{name} must be an integer.")

            if value < 0:
                raise ValueError(f"{name} can't be negative.")
            
            kwargs[name] = value
        
        return self._replace(**kwargs)


