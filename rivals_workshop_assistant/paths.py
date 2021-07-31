import functools
import sys
from pathlib import Path


@functools.lru_cache
def get_exe_path():
    return Path(sys.argv[0])


ASSISTANT_FOLDER = Path("assistant")
ASSISTANT_EXE_NAME = "rivals_workshop_assistant.exe"
ASSISTANT_TMP_EXE_NAME = "rivals_workshop_assistant.exe_"

SPRITES_FOLDER = Path("sprites")
SCRIPTS_FOLDER = Path("scripts")
ATTACKS_FOLDER = SCRIPTS_FOLDER / Path("attacks")
ANIMS_FOLDER = Path("anims")

REPO_OWNER = "Rivals-Workshop-Community-Projects"
ASSISTANT_REPO_NAME = "rivals-workshop-assistant"
LIBRARY_REPO_NAME = "injector-library"
INJECT_FOLDER = ASSISTANT_FOLDER / Path(".inject")
USER_INJECT_FOLDER = ASSISTANT_FOLDER / Path("user_inject")

BACKUP_FOLDER = ASSISTANT_FOLDER / Path("backups")

LOCKFILE_PATH = ASSISTANT_FOLDER / Path(".lock")

PATHS_TO_BACK_UP = [SPRITES_FOLDER, SCRIPTS_FOLDER, ANIMS_FOLDER]

ASEPRITE_LUA_SCRIPTS_FOLDER = Path("lua_scripts")
