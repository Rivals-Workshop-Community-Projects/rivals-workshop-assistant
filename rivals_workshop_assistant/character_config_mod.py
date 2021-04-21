from pathlib import Path
from configparser import ConfigParser

FILENAME = "config.ini"
PATH = FILENAME

SMALL_SPRITES_FIELD = "small_sprites"


def read(root_dir: Path) -> ConfigParser:
    """Controller"""
    config = ConfigParser()
    config.read(root_dir / PATH)
    return config
