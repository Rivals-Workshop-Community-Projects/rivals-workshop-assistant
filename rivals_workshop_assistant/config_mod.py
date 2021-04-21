import enum
from pathlib import Path

import rivals_workshop_assistant.info_files as info_files
from rivals_workshop_assistant.paths import ASSISTANT_FOLDER

FILENAME = "assistant_config.ini"
PATH = ASSISTANT_FOLDER / FILENAME

ASEPRITE_PATH_FIELD = "aseprite_path"


class UpdateConfig(enum.Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    NONE = "none"


UPDATE_LEVEL_FIELD = "update_level"
UPDATE_LEVEL_DEFAULT = UpdateConfig.PATCH


def read_config(root_dir: Path) -> dict:
    """Controller"""
    return info_files.read(root_dir / PATH)


DEFAULT_CONFIG = fr"""\
{UPDATE_LEVEL_FIELD}: {UPDATE_LEVEL_DEFAULT.value}
    # What kind of library updates to allow. 
    # {UpdateConfig.MAJOR.value} = All updates are allowed, even if they may 
    #   break existing code.
    # {UpdateConfig.MINOR.value} = Don't allow breaking changes to existing 
    #   functions, but do allow new functions. Could cause name collisions.
    # {UpdateConfig.PATCH.value} = Only allow changes to existing functions 
    #   that fix bugs or can't break current functionality.
    # {UpdateConfig.NONE.value} = No updates.
    
# {ASEPRITE_PATH_FIELD}: <REPLACE ME, and remove # from beginning of this line>
    # Point this to your Aseprite.exe absolute path, for example: C:\Program Files\Aseprite\aseprite.exe
    # This is needed for the assistant to automatically export your animations to spritesheets.
    # If you use Steam for Aseprite, you can find the path with:
    #   1. The aseprite page of your library
    #   2. The gear icon at the top right
    #   3. Manage
    #   4. Browse Local Files\
    #   5. Copy the path of Aseprite.exe
"""
