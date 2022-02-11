import asyncio
import os
from enum import Enum
from typing import List
import datetime
import sys
from pathlib import Path

from loguru import logger
from notifiers.logging import NotificationHandler

from rivals_workshop_assistant.filelock import FileLock
from rivals_workshop_assistant import (
    updating,
    assistant_config_mod,
    dotfile_mod,
    character_config_mod,
    paths,
)
from rivals_workshop_assistant.character_config_mod import get_has_small_sprites
from rivals_workshop_assistant.dotfile_mod import (
    update_dotfile_after_saving,
)
from rivals_workshop_assistant.paths import LOGS_FOLDER, ASSISTANT_FOLDER
from rivals_workshop_assistant.script_mod import (
    read_scripts,
    Script,
    read_user_inject,
    read_lib_inject,
)
from rivals_workshop_assistant.aseprite_handling import (
    Anim,
    AsepriteConfigParams,
    AsepritePathParams,
)
from rivals_workshop_assistant.aseprite_handling.aseprites import read_aseprites
from rivals_workshop_assistant.aseprite_handling.anims import (
    get_anims,
    save_anims,
)
from rivals_workshop_assistant.file_handling import save_scripts
from rivals_workshop_assistant.assistant_config_mod import (
    get_aseprite_program_path,
    get_hurtboxes_enabled,
    get_is_ssl,
)
from rivals_workshop_assistant.asset_handling import get_required_assets, save_assets
from rivals_workshop_assistant.setup import (
    make_basic_folder_structure,
    get_assistant_folder_exists,
)
from rivals_workshop_assistant.injection import (
    handle_injection,
    freshen_scripts_with_modified_dependencies,
)
from rivals_workshop_assistant.code_generation import handle_codegen
from rivals_workshop_assistant.warning_handling import handle_warning

__version__ = "1.2.19"


class Mode(Enum):
    ALL = "all"
    ANIMS = "anims"
    SCRIPTS = "scripts"


def do_first_run():
    print(
        """\
FIRST TIME SETUP
An `assistant` folder should have been created for you.
Stopping now so you have a chance to edit `assistant/assistant_config.yaml`.
Next time, the assistant will run normally. 
"""
    )


async def main(
    exe_dir: Path,
    given_dir: Path,
    guarantee_root_dir: bool = False,
    mode: Mode = Mode.ALL,
):
    """Runs all processes on scripts in the root_dir
    If guarantee_root_dir is true, it won't backtrack to find the root directory."""
    if guarantee_root_dir:
        root_dir = given_dir
    else:
        root_dir = get_root_dir(given_dir)

    is_first_run = not get_assistant_folder_exists(root_dir)
    make_basic_folder_structure(exe_dir, root_dir)
    if is_first_run:
        do_first_run()
        return

    setup_logger(root_dir=root_dir)
    logger.info(f"Assistant Version: {__version__}")

    lock = FileLock(root_dir / paths.LOCKFILE_PATH)
    try:
        with lock.acquire(timeout=2):
            await update_files(exe_dir=exe_dir, root_dir=root_dir, mode=mode)
    except TimeoutError:
        logger.warning(
            "Attempted to run assistant while an instance was already running. "
            "Consider deleting assistant/.lock if you believe this is in error."
        )
    logger.info("Complete")


def handle_scripts(
    root_dir: Path,
    scripts: List[Script],
    anims: List[Anim],
    assistant_config: dict,
    dotfile: dict,
):
    handle_warning(assistant_config=assistant_config, scripts=scripts)
    handle_codegen(scripts)
    handle_injection(root_dir=root_dir, scripts=scripts, anims=anims, dotfile=dotfile)


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


async def update_files(exe_dir: Path, root_dir: Path, mode: Mode.ALL):
    # todo refactor this
    dotfile, assistant_config, character_config = await read_core_files(root_dir)
    logger.info(f"Dotfile is {dotfile}")

    await updating.update(
        exe_dir=exe_dir, root_dir=root_dir, dotfile=dotfile, config=assistant_config
    )

    scripts = read_scripts(root_dir, dotfile)

    user_inject_scripts = read_user_inject(root_dir, dotfile)
    lib_inject_scripts = read_lib_inject(root_dir, dotfile)

    freshen_scripts_with_modified_dependencies(
        dotfile,
        scripts=scripts,
        inject_scripts=user_inject_scripts + lib_inject_scripts,
    )

    aseprites = read_aseprites(
        root_dir=root_dir,
        dotfile=dotfile,
        assistant_config=assistant_config,
    )
    anims = get_anims(aseprites)

    seen_files = []
    if mode in (mode.ALL, mode.SCRIPTS):
        handle_scripts(
            root_dir=root_dir,
            scripts=scripts,
            assistant_config=assistant_config,
            anims=anims,
            dotfile=dotfile,
        )
        save_scripts(root_dir, scripts)
        seen_files += scripts

    if mode in (mode.ALL, mode.ANIMS):
        await save_anims(
            path_params=AsepritePathParams(
                exe_dir=exe_dir,
                root_dir=root_dir,
                aseprite_program_path=get_aseprite_program_path(assistant_config),
            ),
            config_params=AsepriteConfigParams(
                has_small_sprites=get_has_small_sprites(
                    scripts=scripts, character_config=character_config
                ),
                hurtboxes_enabled=get_hurtboxes_enabled(config=assistant_config),
                is_ssl=get_is_ssl(config=assistant_config),
            ),
            aseprites=aseprites,
        )
        seen_files += aseprites

    update_dotfile_after_saving(
        now=datetime.datetime.now(),
        dotfile=dotfile,
        seen_files=seen_files + user_inject_scripts,
    )

    assets = get_required_assets(scripts)
    await save_assets(root_dir, assets)

    dotfile_mod.save_dotfile(root_dir, dotfile)


def get_root_dir(given_dir: Path) -> Path:
    """Return the absolute path to the character's root directory, containing
    their config file.
    Currently assumes that that path is passed as the first argument"""
    if "config.ini" in [path.name for path in given_dir.glob("*")]:
        return given_dir
    else:
        file_names = "\n".join([path.name for path in given_dir.glob("*")])
        raise FileNotFoundError(
            f"""Given folder does not contain config.ini.
Current directory is: {given_dir}
Files in current directory are: {file_names}"""
        )


def setup_logger(root_dir: Path):
    logger.add(
        root_dir / ASSISTANT_FOLDER / LOGS_FOLDER / f"assistant_{{time}}.log",
        retention="2 days",
        backtrace=True,
        diagnose=True,
    )
    logger.add(sys.stdout, level="WARNING")

    try:
        from rivals_workshop_assistant.secrets import SLACK_WEBHOOK

        handler = NotificationHandler("slack", defaults={"webhook_url": SLACK_WEBHOOK})
        logger.add(handler, level="ERROR")
    except ImportError:
        logger.warning("Secrets file not present")


@logger.catch
def run_main(
    exe_dir: Path,
    project_dir: Path,
    guarantee_root_dir: bool = False,
    mode: Mode = Mode.ALL,
):
    logger.info(f"Exe dir: {exe_dir}")
    logger.info(f"Project dir: {project_dir}")
    logger.info(f"Mode: {mode.name}")

    asyncio.run(
        main(
            exe_dir=exe_dir,
            given_dir=project_dir,
            guarantee_root_dir=guarantee_root_dir,
            mode=mode,
        )
    )


if __name__ == "__main__":
    exe_dir = Path(sys.argv[0]).parent.absolute()
    project_dir = Path(sys.argv[1]).absolute()
    try:
        mode_value = sys.argv[2]
        try:
            mode = Mode(mode_value)
        except ValueError:
            logger.error(
                f"Invalid mode argument. f{mode_value}"
                f"Valid modes are {[mode.name for mode in Mode]}"
            )
            mode = Mode.ALL
    except IndexError:
        # Argument not passed. Use default.
        mode = Mode.ALL

    try:
        run_main(exe_dir=exe_dir, project_dir=project_dir, mode=mode)
    except Exception as e:
        # This may be no longer needed because of @logger.catch
        import traceback

        print(e)
        print("".join(traceback.format_tb(e.__traceback__)))
