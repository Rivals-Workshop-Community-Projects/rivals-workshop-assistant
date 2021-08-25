import enum
import typing
from pathlib import Path

import rivals_workshop_assistant.info_files as info_files
from rivals_workshop_assistant.paths import ASSISTANT_FOLDER

if typing.TYPE_CHECKING:
    from rivals_workshop_assistant.aseprite_handling import TagColor

FILENAME = "assistant_config.yaml"
PATH = ASSISTANT_FOLDER / FILENAME

ASEPRITE_PATH_FIELD = "aseprite_path"


def read_project_config(root_dir: Path) -> dict:
    """Controller"""
    return info_files.read(root_dir / PATH)


def make_default_override(exe_dir: Path, content: str):
    info_files.create_file(path=(exe_dir / FILENAME), content=content)


def read_default_override(exe_dir: Path) -> dict:
    """Read the config from the exe directory, used to overwrite the default config"""
    return info_files.read(exe_dir / FILENAME)


def overwrite_default_config(
    initial_default_config: dict, user_default_config_override: dict
) -> dict:
    result = initial_default_config.copy()
    result.update(user_default_config_override)
    return result


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


WARNINGS_FIELD = "warnings"
WARNING_DESYNC_OBJECT_VAR_SET_IN_DRAW_SCRIPT_VALUE = (
    "desync_object_var_set_in_draw_script"
)
WARNING_DESYNC_UNSAFE_CAMERA_READ_VALUE = "desync_unsafe_camera_read"
WARNING_CHECK_WINDOW_TIMER_WITHOUT_CHECK_HITPAUSE = (
    "check_window_timer_without_check_hitpause"
)
WARNING_RECURSIVE_SET_ATTACK = "recursive_set_attack"


def get_initial_default_config() -> dict:
    return info_files.YAML_HANDLER.load(DEFAULT_CONFIG)


def override_default_config(default_config, user_default_config_override):
    raise NotImplementedError


GENERATE_HURTBOXES_FIELD = "generate_hurtboxes"
GENERATE_HURTBOXES_DEFAULT = True


def get_hurtboxes_enabled(config: dict):
    return config.get(GENERATE_HURTBOXES_FIELD, GENERATE_HURTBOXES_DEFAULT)


DEFAULT_CONFIG = f"""\
# Format is <key name>: <value> (with a space after the : )
# E.g.
# update_level: patch
  
{ASEPRITE_PATH_FIELD}: # FILL THIS IN TO USE ASEPRITE
    # Point this to your Aseprite.exe absolute path, for example: 
    # aseprite_path: C:/Program Files/Aseprite/aseprite.exe
    # This is needed for the assistant to automatically export your animations to spritesheets.
    # If you use Steam for Aseprite, you can find the path with:
    #   The aseprite page of your library, The gear icon at the top right,
    #   Manage, Browse Local Files, Copy the path of Aseprite.exe to the config.
    #
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

{GENERATE_HURTBOXES_FIELD}: {GENERATE_HURTBOXES_DEFAULT}
    # If the assistant should automatically generate hurtboxes from your anim files.
    # See https://rivalslib.com/assistant/animation_handling.html#hurtbox-generation

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
    #
{WARNINGS_FIELD}: 
- {WARNING_DESYNC_OBJECT_VAR_SET_IN_DRAW_SCRIPT_VALUE}
- {WARNING_DESYNC_UNSAFE_CAMERA_READ_VALUE}
- {WARNING_CHECK_WINDOW_TIMER_WITHOUT_CHECK_HITPAUSE}
- {WARNING_RECURSIVE_SET_ATTACK}
    # Comment out any warnings you want to disable with `#`.
    # Learn more about warnings at https://rivalslib.com/assistant/warnings/
"""


def get_aseprite_path(assistant_config: dict) -> typing.Optional[Path]:
    path_string = assistant_config.get(ASEPRITE_PATH_FIELD, None)
    if path_string:
        return Path(path_string)
    else:
        return None
