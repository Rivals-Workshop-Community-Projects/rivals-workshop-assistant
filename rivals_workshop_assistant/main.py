import sys
from pathlib import Path

from rivals_workshop_assistant.asset_handling import get_required_assets, save_assets
from rivals_workshop_assistant.codegen import handle_codegen
from rivals_workshop_assistant.injection import handle_injection

Scripts = dict[Path, str]


def main(root_dir):
    """Runs all processes on scripts in the root_dir"""
    scripts = read_scripts(root_dir)

    scripts = handle_codegen(scripts)
    scripts = handle_injection(scripts)

    save_scripts(root_dir, scripts)

    assets = get_required_assets(scripts)
    save_assets(root_dir, assets)


def get_root_dir() -> Path:
    """Return the absolute path to the character's root directory, containing their config file.
    Currently assumes that that path is passed as the first argument"""
    # Todo, if config is not in current file, keep searching parent directory
    return Path(sys.argv[0])


def read_scripts(root_dir: Path) -> Scripts:
    gml_paths = list((root_dir / 'scripts').rglob('*.gml'))
    scripts = {gml_path: gml_path.read_text()
               for gml_path in gml_paths}

    return scripts


def save_scripts(root_dir: Path, scripts: Scripts):
    raise NotImplementedError


if __name__ == '__main__':
    root_dir = get_root_dir()
    main(root_dir)
