import datetime
import sys
import typing
from pathlib import Path

from .script_mod import Script
from .asset_handling import get_required_assets, save_assets
from .setup import make_basic_folder_structure
from .injection import handle_injection
from .code_generation import handle_codegen
from .dotfile_mod import read_dotfile, yaml_load


def main(given_dir: Path):
    """Runs all processes on scripts in the root_dir"""
    root_dir = get_root_dir(given_dir)
    make_basic_folder_structure(root_dir)

    scripts = read_scripts(root_dir)

    scripts = handle_codegen(scripts)
    scripts = handle_injection(root_dir, scripts)

    save_scripts(root_dir, scripts)

    assets = get_required_assets(scripts)
    save_assets(root_dir, assets)


def get_root_dir(given_dir: Path) -> Path:
    """Return the absolute path to the character's root directory, containing
    their config file.
    Currently assumes that that path is passed as the first argument"""
    if "config.ini" in [path.name for path in given_dir.glob("*")]:
        return given_dir
    else:
        raise FileNotFoundError("Given folder does not contain config.ini. Aborting.")
        # Todo,
        #  if config is not in current file, keep searching parent directory


def _get_processed_time_register(root_dir: Path) -> dict[Path, datetime.datetime]:
    dotfile = read_dotfile(root_dir)  # TODO this and yaml load should be combined?

    yaml = yaml_load(dotfile)

    # TODO make absolute

    return yaml


def get_processed_time(
    processed_time_register: dict[Path, datetime.datetime], path: Path
) -> typing.Optional[Script]:
    return processed_time_register.get(path, None)


def read_scripts(root_dir: Path) -> list[Script]:
    """Returns all Scripts in the scripts directory."""
    gml_paths = list((root_dir / "scripts").rglob("*.gml"))

    processed_time_register = _get_processed_time_register(root_dir)

    scripts = []
    for gml_path in gml_paths:
        script = Script(
            path=gml_path,
            original_content=gml_path.read_text(),
            modified_time=datetime.datetime.fromtimestamp(gml_path.stat().st_mtime),
            processed_time=get_processed_time(processed_time_register, gml_path),
        )
        scripts.append(script)

    return scripts


def save_scripts(root_dir: Path, scripts: list[Script]):
    for script in scripts:
        script.save(root_dir)


if __name__ == "__main__":
    root_dir = Path(sys.argv[1])
    main(root_dir)
