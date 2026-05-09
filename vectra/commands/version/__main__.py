"""# vectra.commands.version.main

Main process etry point for `vectra version` command.
"""

__all__ = ["version_entry_point"]

from vectra.commands.version.__args__   import VersionConfig
from vectra.registration                import register_command

@register_command(
    id =        "version",
    config =    VersionConfig
)
def version_entry_point(*args, **kwargs) -> None:
    """# Display Package Version Information."""
    # Import banner.
    from vectra.utilities   import BANNER

    # Display banner.
    print(BANNER[1:])