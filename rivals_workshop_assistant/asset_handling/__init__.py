from pathlib import Path

from rivals_workshop_assistant.script_mod import Script
from .asset_types import Asset, ASSET_TYPES
from typing import List, Set


def get_required_assets(scripts: List[Script]) -> Set[Asset]:
    """Gets all assets the scripts use, including things that aren't the
    assistant's responsibility.
    Those assets are filtered out in the supply step, after this."""
    required_assets_for_scripts = set()
    for script in scripts:
        if script.is_fresh:
            required_assets_for_scripts.update(_get_required_assets_for_script(script))

    return required_assets_for_scripts


def _get_required_assets_for_script(script: Script) -> Set[Asset]:
    assets = set()
    for asset_type in ASSET_TYPES:
        assets.update(asset_type.get_from_text(script.working_content))
    return assets


async def save_assets(root_dir: Path, assets: Set[Asset]):
    """Controller"""
    for asset in assets:
        await asset.supply(root_dir)
