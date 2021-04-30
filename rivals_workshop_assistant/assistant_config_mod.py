import enum
from pathlib import Path

import rivals_workshop_assistant.info_files as info_files
from rivals_workshop_assistant.paths import ASSISTANT_FOLDER

FILENAME = "assistant_config.yaml"
PATH = ASSISTANT_FOLDER / FILENAME

ASEPRITE_PATH_FIELD = "aseprite_path"


class UpdateLevel(enum.Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    NONE = "none"


LIBRARY_UPDATE_LEVEL_FIELD = "library_update_level"
LIBRARY_UPDATE_LEVEL_DEFAULT = UpdateLevel.PATCH


def get_library_update_level(config: dict) -> UpdateLevel:
    return UpdateLevel(
        config.get(LIBRARY_UPDATE_LEVEL_FIELD, LIBRARY_UPDATE_LEVEL_DEFAULT)
    )


ASSISTANT_SELF_UPDATE_FIELD = "assistant_should_self_update"
ASSISTANT_SELF_UPDATE_DEFAULT = True


def get_assistant_self_update(config: dict) -> bool:
    return config.get(ASSISTANT_SELF_UPDATE_FIELD, ASSISTANT_SELF_UPDATE_DEFAULT)


ANIM_TAG_COLOR_FIELD = "anim_tag_color"
ANIM_TAG_COLOR_DEFAULT = "blue"

WINDOW_TAG_COLOR_FIELD = "window_tag_color"
WINDOW_TAG_COLOR_DEFAULT = "red"


def get_anim_tag_color(config: dict) -> "TagColor":
    return config.get(ANIM_TAG_COLOR_FIELD, ANIM_TAG_COLOR_DEFAULT)


def get_window_tag_color(config: dict) -> "TagColor":
    return config.get(WINDOW_TAG_COLOR_FIELD, WINDOW_TAG_COLOR_DEFAULT)


def read(root_dir: Path) -> dict:
    """Controller"""
    return info_files.read(root_dir / PATH)


DEFAULT_CONFIG = f"""\
# Format is <key name>: <value> (with a space after the : )
# E.g.
# update_level: patch
  
# {ASEPRITE_PATH_FIELD}: <REPLACE ME, and remove # from beginning of this line>
    # Point this to your Aseprite.exe absolute path, for example: 
    # aseprite_path: C:/Program Files/Aseprite/aseprite.exe
    # This is needed for the assistant to automatically export your animations to spritesheets.
    # If you use Steam for Aseprite, you can find the path with:
    #   The aseprite page of your library, The gear icon at the top right,
    #   Manage, Browse Local Files, Copy the path of Aseprite.exe to the config.
    
    
    # Aseprite Tag Color Configs
    # Legal values are:
    #   black, red, orange, yellow, green, blue, purple, gray
{ANIM_TAG_COLOR_FIELD}: {ANIM_TAG_COLOR_DEFAULT}
    # The color of Aseprite tag representing an animation. 
    # If you keep multiple aseprite animations in a file, put each in a tag with this 
    # color, and the assistant will export them under that tag's name.
{WINDOW_TAG_COLOR_FIELD}: {WINDOW_TAG_COLOR_DEFAULT}
    # The color of Aseprite tag representing an attack window.
    # If a tag of this color is found, it will be used to add animation meta-data to the 
    # bottom of the attack's script.

{LIBRARY_UPDATE_LEVEL_FIELD}: {LIBRARY_UPDATE_LEVEL_DEFAULT.value}
    # What kind of library updates to allow. 
    # This only affects the functions available to inject, not assistant behavior.
    # {UpdateLevel.MAJOR.value} = All updates are allowed, even if they may 
    #   break existing code.
    # {UpdateLevel.MINOR.value} = Don't allow breaking changes to existing 
    #   functions, but do allow new functions. Could cause name collisions.
    # {UpdateLevel.PATCH.value} = Only allow changes to existing functions 
    #   that fix bugs or can't break current functionality.
    # {UpdateLevel.NONE.value} = No updates.
    
{ASSISTANT_SELF_UPDATE_FIELD}: {ASSISTANT_SELF_UPDATE_DEFAULT}
    # If the assistant should automatically receive behavior updates.
"""
