from pathlib import Path

import rivals_workshop_assistant.assistant_config_mod
import rivals_workshop_assistant.paths
from rivals_workshop_assistant import paths as paths
from rivals_workshop_assistant.info_files import _yaml_dumps
from rivals_workshop_assistant.injection.installation import (
    ANIMS_FOLDER_README,
)
from rivals_workshop_assistant.assistant_config_mod import (
    make_default_override,
    get_initial_default_config,
    read_default_override,
    overwrite_default_config,
)
from rivals_workshop_assistant.file_handling import create_file


def make_user_inject_folder(root_dir: Path):
    (root_dir / rivals_workshop_assistant.paths.USER_INJECT_FOLDER).mkdir(
        parents=True, exist_ok=True
    )


def make_anims_folder(root_dir: Path):
    (root_dir / paths.ANIMS_FOLDER).mkdir(parents=True, exist_ok=True)
    create_file(
        path=(root_dir / paths.ANIMS_FOLDER / "readme.md"), content=ANIMS_FOLDER_README
    )


def make_default_config(root_dir: Path, default_config: str):
    create_file(
        path=(root_dir / rivals_workshop_assistant.assistant_config_mod.PATH),
        content=default_config,
    )


def make_basic_folder_structure(exe_dir: Path, root_dir: Path):
    make_user_inject_folder(root_dir)
    make_anims_folder(root_dir)

    initial_default_config = get_initial_default_config()
    make_default_override(exe_dir, _yaml_dumps(initial_default_config))
    user_default_config_override = read_default_override(exe_dir)

    default_config = overwrite_default_config(
        initial_default_config, user_default_config_override
    )
    make_default_config(root_dir, _yaml_dumps(default_config))

    create_file(path=(root_dir / paths.LOCKFILE_PATH), content="")
