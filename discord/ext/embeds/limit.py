from typing import NamedTuple

from discord.utils import MISSING


class _EmbedLimits(NamedTuple):
    title: int
    description: int
    fields: int
    field_name: int
    field_value: int
    footer_text: int
    author_name: int

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
