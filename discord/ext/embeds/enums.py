from discord.enums import Enum


class EmbedMediaType(Enum):
    """Represents the type of media in an embed."""

    image = "image"
    """Media is an image."""
    video = "video"
    """Media is a video."""
    thumbnail = "thumbnail"
    """Media is a thumbnail."""
    footer_icon = "footer_icon"
    """Media is a footer icon."""
    author_icon = "author_icon"
    """Media is an author icon."""


class MultiImagesType(Enum):
    """Represents the input for the ``type`` field of :class:`Embed.with_multiple_images`."""

    image = "image"
    """The input is an image."""
    thumbnail = "thumbnail"
    """The input is a thumbnail."""
