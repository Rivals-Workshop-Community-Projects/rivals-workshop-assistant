from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunContext:
    exe_dir: Path
    root_dir: Path
    dotfile: dict
    assistant_config: dict
    character_config: dict
