from discord import DiscordException

__all__ = ("LimitReached",)


class LimitReached(DiscordException):
    """Exception raised when the maximum number of x is reached."""

    def __init__(
        self,
        limit_of: str,
        limit: int,
        current: int,
    ) -> None:
        self.limit_of = limit_of
        self.limit = limit
        self.current = current

        KWARG_INFO = "You can set check_limits to False in Embed() to disable this check."
        DISCLAIMER = (
            "Note that the limit is hardcoded and may have changed since the last update. "
            f"Please open an issue if you think this is the case. Thank you!\n{KWARG_INFO}"
        )
        super().__init__(f"The limit of {limit_of} was reached ({current}/{limit}).\nDisclaimer: {DISCLAIMER}")
