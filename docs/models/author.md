# EmbedAuthor
Object representing the ``author`` field of an embed.

## Usage
- ``author`` \
Attribute of Embed that can be set or a parameter of the constructor.

## Parameters

- ``name`` (required): str  \
The name of the author.
- ``icon_url`` (required): str \
The icon url of the author. The cannot be used with ``file_url``.
- ``url``: str \
The url of the author.
- ``file_url``: discord.File \
The file url of the author. The cannot be used with ``icon_url``.
- ``proxy_icon_url``: str \
The proxy icon url of the author.

## Methods

- ``from_user`` \
Creates an EmbedAuthor from a discord.User or discord.Member object.
