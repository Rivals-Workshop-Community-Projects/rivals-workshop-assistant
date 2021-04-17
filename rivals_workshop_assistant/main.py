import sys
from pathlib import Path

from rivals_workshop_assistant.script_mod import Script
from rivals_workshop_assistant.asset_handling import get_required_assets, save_assets
from rivals_workshop_assistant.setup import make_basic_folder_structure
from rivals_workshop_assistant.injection import handle_injection
from rivals_workshop_assistant.code_generation import handle_codegen


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


def read_scripts(root_dir: Path) -> list[Script]:
    """Returns path:content dict for files that have been modified since last
    process."""
    gml_paths = list((root_dir / "scripts").rglob("*.gml"))
    scripts = [
        Script(
            path=gml_path,
            original_content=gml_path.read_text(),
            modified_time=None,
            processed_time=None,
        )
        for gml_path in gml_paths
    ]
    # todo add time handling to this

    return scripts


def save_scripts(root_dir: Path, scripts: list[Script]):
    for script in scripts:
        script.save(root_dir)


if __name__ == "__main__":
    root_dir = Path(sys.argv[1])
    main(root_dir)
