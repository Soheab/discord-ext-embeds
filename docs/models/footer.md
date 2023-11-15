# EmbedFooter
Object representing the ``footer`` field of an embed.

## Usage
- ``footer`` \
Attribute of Embed that can be set or a parameter of the constructor.

## Parameters

- ``text`` (required): str  \
The name of the footer.
- ``icon_url`` (required): str \
The icon url of the footer. The cannot be used with ``file_url``.
- ``file_url``: Optional[discord.File] \
The file url of the footer. The cannot be used with ``icon_url``.
- ``proxy_icon_url``: str \
The proxy icon url of the footer. This is returned by the API. You can't
set it anyways.

## Methods

- ``from_user`` \
Creates an EmbedFooter from a discord.User or discord.Member object.

