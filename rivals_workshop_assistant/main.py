import datetime
import itertools
import sys
import typing
from pathlib import Path

from rivals_workshop_assistant.injection.installation import ASEPRITE_PATH_NAME
from .script_mod import Script, Anim, File
from .asset_handling import get_required_assets, save_assets
from .setup import make_basic_folder_structure
from .injection import handle_injection
from .code_generation import handle_codegen
import rivals_workshop_assistant.info_files as info_files


def main(given_dir: Path):
    """Runs all processes on scripts in the root_dir"""
    root_dir = get_root_dir(given_dir)
    make_basic_folder_structure(root_dir)
    dotfile = info_files.read_dotfile(root_dir)
    config = info_files.read_config(root_dir)

    scripts = read_scripts(root_dir, dotfile)
    anims = read_anims(root_dir, dotfile)

    scripts = handle_codegen(scripts)
    scripts = handle_injection(root_dir, dotfile, scripts)

    save_scripts(root_dir, scripts)

    aseprite_path = config.get(ASEPRITE_PATH_NAME, None)
    save_anims(root_dir, aseprite_path, anims)
    update_dotfile_after_saving(
        now=datetime.datetime.now(), dotfile=dotfile, files=scripts + anims
    )

    assets = get_required_assets(scripts)
    save_assets(root_dir, assets)

    info_files.save_dotfile(root_dir, dotfile)


def get_root_dir(given_dir: Path) -> Path:
    """Return the absolute path to the character's root directory, containing
    their config file.
    Currently assumes that that path is passed as the first argument"""
    if "config.ini" in [path.name for path in given_dir.glob("*")]:
        return given_dir
    else:
        raise FileNotFoundError("Given folder does not contain config.ini. Aborting.")


def get_processed_time(dotfile: dict, path: Path) -> typing.Optional[datetime.datetime]:
    if path in dotfile.get(info_files.SEEN_FILES, []):
        return dotfile.get(info_files.PROCESSED_TIME, None)
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
            original_content=path.read_text(),
            modified_time=_get_modified_time(path),
            processed_time=get_processed_time(dotfile=dotfile, path=path),
        )
        scripts.append(script)

    return scripts


def read_anims(root_dir: Path, dotfile: dict) -> list[Anim]:
    ase_paths = itertools.chain(
        *[
            list((root_dir / "anims").rglob(f"*.{filetype}"))
            for filetype in ("ase", "aseprite")
        ]
    )

    anims = []
    for path in ase_paths:
        anim = Anim(
            path=path,
            modified_time=_get_modified_time(path),
            processed_time=get_processed_time(dotfile=dotfile, path=path),
        )
        anims.append(anim)
    return anims


def save_scripts(root_dir: Path, scripts: list[Script]):
    for script in scripts:
        script.save(root_dir)


def save_anims(root_dir: Path, aseprite_path: Path, anims: list[Anim]):
    if aseprite_path:
        for anim in anims:
            anim.save(root_dir, aseprite_path)  # todo add small_sprites compatibility


def update_dotfile_after_saving(
    dotfile: dict, now: datetime.datetime, files: list[File]
):
    dotfile[info_files.PROCESSED_TIME] = now
    dotfile[info_files.SEEN_FILES] = [file.path.as_posix() for file in files]


if __name__ == "__main__":
    root_dir = Path(sys.argv[1])
    main(root_dir)
