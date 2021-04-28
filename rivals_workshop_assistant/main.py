import re
from configparser import ConfigParser
import datetime
import itertools
import sys
import typing
from pathlib import Path

import rivals_workshop_assistant.updating
from rivals_workshop_assistant import (
    assistant_config_mod,
    dotfile_mod,
    character_config_mod,
)
from rivals_workshop_assistant.assistant_config_mod import ASEPRITE_PATH_FIELD
from rivals_workshop_assistant.script_mod import Script, Aseprite, File
from rivals_workshop_assistant.asset_handling import get_required_assets, save_assets
from rivals_workshop_assistant.setup import make_basic_folder_structure
from rivals_workshop_assistant.injection import handle_injection
from rivals_workshop_assistant.code_generation import handle_codegen


def main(given_dir: Path):
    """Runs all processes on scripts in the root_dir"""
    root_dir = get_root_dir(given_dir)
    make_basic_folder_structure(root_dir)
    dotfile = dotfile_mod.read(root_dir)
    assistant_config = assistant_config_mod.read(root_dir)
    character_config = character_config_mod.read(root_dir)

    rivals_workshop_assistant.updating.update(
        root_dir=root_dir, dotfile=dotfile, config=assistant_config
    )

    scripts = read_scripts(root_dir, dotfile)
    aseprites = read_aseprites(root_dir, dotfile)

    scripts = handle_codegen(scripts)
    scripts = handle_injection(
        root_dir=root_dir,
        scripts=scripts,
    )

    save_scripts(root_dir, scripts)

    save_aseprites(
        root_dir,
        aseprite_path=get_aseprite_path(assistant_config),
        aseprites=aseprites,
        has_small_sprites=get_has_small_sprites(
            scripts=scripts, character_config=character_config
        ),
    )
    update_dotfile_after_saving(
        now=datetime.datetime.now(), dotfile=dotfile, files=scripts + aseprites
    )

    assets = get_required_assets(scripts)
    save_assets(root_dir, assets)

    dotfile_mod.save_dotfile(root_dir, dotfile)


def get_aseprite_path(assistant_config: dict) -> typing.Optional[Path]:
    path_string = assistant_config.get(ASEPRITE_PATH_FIELD, None)
    if path_string:
        return Path(path_string)
    else:
        return None


def get_root_dir(given_dir: Path) -> Path:
    """Return the absolute path to the character's root directory, containing
    their config file.
    Currently assumes that that path is passed as the first argument"""
    if "config.ini" in [path.name for path in given_dir.glob("*")]:
        return given_dir
    else:
        file_names = "\n".join([path.name for path in given_dir.glob("*")])
        raise FileNotFoundError(
            f"""Given folder does not contain config.ini.
Current directory is: {given_dir}
Files in current directory are: {file_names}"""
        )


def get_processed_time(dotfile: dict, path: Path) -> typing.Optional[datetime.datetime]:
    seen_files = dotfile.get(dotfile_mod.SEEN_FILES_FIELD, [])
    if seen_files is None:
        seen_files = []
    if path.as_posix() in seen_files:
        return dotfile.get(dotfile_mod.PROCESSED_TIME_FIELD, None)
    else:
        return None


def _get_modified_time(path: Path) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(path.stat().st_mtime)


def read_scripts(root_dir: Path, dotfile: dict) -> list[Script]:
    """Returns all Scripts in the scripts directory."""
    gml_paths = list((root_dir / "scripts").rglob("*.gml"))

    scripts = []
    for path in gml_paths:
        script = Script(
            path=path,
            original_content=path.read_text(encoding="UTF8", errors="surrogateescape"),
            modified_time=_get_modified_time(path),
            processed_time=get_processed_time(dotfile=dotfile, path=path),
        )
        scripts.append(script)

    return scripts


def read_aseprites(root_dir: Path, dotfile: dict) -> list[Aseprite]:
    ase_paths = itertools.chain(
        *[
            list((root_dir / "anims").rglob(f"*.{filetype}"))
            for filetype in ("ase", "aseprite")
        ]
    )

    aseprites = []
    for path in ase_paths:
        aseprite = Aseprite(
            path=path,
            modified_time=_get_modified_time(path),
            processed_time=get_processed_time(dotfile=dotfile, path=path),
        )
        aseprites.append(aseprite)
    return aseprites


def save_scripts(root_dir: Path, scripts: list[Script]):
    for script in scripts:
        script.save(root_dir)


def save_aseprites(
    root_dir: Path,
    aseprite_path: Path,
    aseprites: list[Aseprite],
    has_small_sprites: bool,
):
    if not aseprite_path:
        return
    for aseprite in aseprites:
        if aseprite.is_fresh:
            aseprite.save(
                root_dir=root_dir,
                aseprite_path=aseprite_path,
                has_small_sprites=has_small_sprites,
            )


def update_dotfile_after_saving(
    dotfile: dict, now: datetime.datetime, files: list[File]
):
    dotfile[dotfile_mod.PROCESSED_TIME_FIELD] = now
    dotfile[dotfile_mod.SEEN_FILES_FIELD] = [file.path.as_posix() for file in files]


def get_has_small_sprites(scripts: list[Script], character_config: ConfigParser):
    in_character_config = character_config.get(
        "general", character_config_mod.SMALL_SPRITES_FIELD, fallback=None
    )

    try:
        init_gml = [
            script.working_content
            for script in scripts
            if script.path.name == "init.gml"
        ][0]
    except IndexError:
        init_gml = ""
    match = re.search(pattern=r"small_sprites\s*=\s*(1|true)", string=init_gml)
    return bool(in_character_config) or bool(match)
    # Get character config. Search for 'small_sprites="1"'
    # get init.gml. Search for small_sprites assignment to 1 or true.


if __name__ == "__main__":
    root_dir = Path(sys.argv[1])
    main(root_dir)
