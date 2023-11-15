# discord-ext-embeds
An extension for discord.py that takes embeds to the next level!

## What is this?
discord-ext-embeds is an extension for discord.py that adds a few nice-to-have features to discord.py's embed.

## Features (compared to discord.py's embed)
- Embeds can be created with a single line of code
```py
from discord.ext import embeds
embed = embeds.Embed(
    ..., # kwargs not shown here are the same as discord.Embed
    # Can be a int, str or discord.Color object. Defaults to discord.Color.dark_theme()
    colour=0x00ff00,
    # Can be a string, User/Member object or embeds.EmbedAuthor object.
    author="Author Name",
    # or author=interaction.user,
    # or author=embeds.EmbedAuthor(name="Author Name", icon_url=..., url=...),
    # or author=embeds.EmbedAuthor.from_user(interaction.user),
    footer="Footer",  # same as author but embeds.EmbedFooter instead of embeds.EmbedAuthor
    # Can be a string, discord.File or embeds.EmbedMedia object.
    image="<url>",
    # or image=discord.File("path/to/file"),
    # or image=embeds.EmbedMedia(url="<url>"),
    thumbnail="<url>",  # same as image
)
- Character limit checks
```py
from discord.ext import embeds
embed = embeds.Embed(
    title="something longer than embeds.Embed.LIMITS.title",
    description="something longer than embeds.Embed.LIMITS.description",
    ...
)
```
Note that these limits are hardcoded in this extension and may not be accurate to discord's limits.
You can use embeds.Embed.LIMITS to get the limits for each field or use the ``.edit`` method on it to change one or multiple.
- 

## Installation
```sh
python -m install discord-ext-embeds
```