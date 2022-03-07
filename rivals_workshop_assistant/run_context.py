import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import List

from loguru import logger

from rivals_workshop_assistant import (
    dotfile_mod,
    assistant_config_mod,
    character_config_mod,
)


@dataclass
class RunContext:
    exe_dir: Path
    root_dir: Path
    dotfile: dict
    assistant_config: dict
    character_config: dict


async def make_run_context_from_paths(exe_dir: Path, root_dir: Path) -> RunContext:
    dotfile, assistant_config, character_config = await read_core_files(root_dir)
    run_context = RunContext(
        exe_dir=exe_dir,
        root_dir=root_dir,
        dotfile=dotfile,
        assistant_config=assistant_config,
        character_config=character_config,
    )
    logger.info(f"Dotfile is {dotfile}")
    logger.info(f"assistant config is {assistant_config}")
    logger.info(f"character config is {dict(character_config)}")
    return run_context


async def read_core_files(root_dir: Path) -> List[dict]:
    """Return dotfile, assistant_config, character_config"""
    tasks = [
        asyncio.create_task(coro)
        for coro in [
            dotfile_mod.read(root_dir),
            assistant_config_mod.read_project_config(root_dir),
            character_config_mod.read(root_dir),
        ]
    ]
    return [await task for task in tasks]
