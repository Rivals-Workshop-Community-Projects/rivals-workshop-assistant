from dataclasses import dataclass
from pathlib import Path


@dataclass
class AsepritePathParams:
    exe_dir: Path
    root_dir: Path
    aseprite_program_path: Path


@dataclass
class AsepriteConfigParams:
    has_small_sprites: bool = False
    hurtboxes_enabled: bool = False
    is_ssl: bool = False
