import re
from pathlib import Path
from configparser import ConfigParser
from typing import List

from rivals_workshop_assistant.script_mod import Script

FILENAME = "config.ini"
PATH = FILENAME

SMALL_SPRITES_FIELD = "small_sprites"


def read(root_dir: Path) -> ConfigParser:
    """Controller"""
    config = ConfigParser()
    config.read(root_dir / PATH)
    return config


def get_has_small_sprites(scripts: List[Script], character_config: ConfigParser):
    in_character_config = character_config.get(
        "general", SMALL_SPRITES_FIELD, fallback=None
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
