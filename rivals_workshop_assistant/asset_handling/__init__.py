from pathlib import Path

from rivals_workshop_assistant import paths as paths
from .asset_types import Asset, ASSET_TYPES


def get_required_assets(scripts: paths.Scripts) -> set[Asset]:
    """Gets all assets the scripts use, including things that aren't the
    assistant's responsibility.
    Those assets are filtered out in the supply step, after this."""
    required_assets_for_scripts = set()
    for script in scripts.values():
        required_assets_for_scripts.update(
            _get_required_assets_for_script(script)
        )

    return required_assets_for_scripts


def _get_required_assets_for_script(script) -> set[Asset]:
    assets = set()
    for asset_type in ASSET_TYPES:
        assets.update(asset_type.get_from_text(script))
    return assets


def save_assets(root_dir: Path, assets: set[Asset]):
    """Controller"""
    for asset in assets:
        asset.supply(root_dir)