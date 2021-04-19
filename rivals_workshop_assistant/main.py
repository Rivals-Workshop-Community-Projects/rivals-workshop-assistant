import datetime
import itertools
import sys
import typing
from pathlib import Path

import rivals_workshop_assistant.aseprite_loading
from .script_mod import Script, Anim
from .asset_handling import get_required_assets, save_assets
from .setup import make_basic_folder_structure
from .injection import handle_injection
from .code_generation import handle_codegen
import rivals_workshop_assistant.dotfile_mod as dotfile_mod


def main(given_dir: Path):
    """Runs all processes on scripts in the root_dir"""
    root_dir = get_root_dir(given_dir)
    make_basic_folder_structure(root_dir)
    dotfile = dotfile_mod.read_dotfile(root_dir)

    scripts = read_scripts(root_dir, dotfile)
    anims = read_anims(root_dir, dotfile)

    scripts = handle_codegen(scripts)
    scripts = handle_injection(root_dir, dotfile, scripts)
    save_scripts(root_dir, dotfile, scripts)

    assets = get_required_assets(scripts)
    save_assets(root_dir, assets)

    dotfile_mod.save_dotfile(root_dir, dotfile)


def get_root_dir(given_dir: Path) -> Path:
    """Return the absolute path to the character's root directory, containing
    their config file.
    Currently assumes that that path is passed as the first argument"""
    if "config.ini" in [path.name for path in given_dir.glob("*")]:
        return given_dir
    else:
        raise FileNotFoundError("Given folder does not contain config.ini. Aborting.")


def get_processed_time(dotfile: dict, path: Path) -> typing.Optional[datetime.datetime]:
    if path in dotfile.get(dotfile_mod.SEEN_FILES, []):
        return dotfile.get(dotfile_mod.PROCESSED_TIME, None)
    else:
        return None


def _get_modified_time(path: Path) -> datetime.datetime:
    datetime.datetime.fromtimestamp(path.stat().st_mtime)


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


def save_scripts(root_dir: Path, dotfile: dict, scripts: list[Script]):
    for script in scripts:
        script.save(root_dir)

    now = datetime.datetime.now()
    _update_docfile_after_saving_scripts(dotfile, now, scripts)


def _update_docfile_after_saving_scripts(
    dotfile: dict, now: datetime.datetime, scripts: list[Script]
) -> dict:
    dotfile[dotfile_mod.PROCESSED_TIME] = now
    dotfile[dotfile_mod.SEEN_FILES] = [script.path.as_posix() for script in scripts]
    return dotfile


if __name__ == "__main__":
    root_dir = Path(sys.argv[1])
    main(root_dir)
