import asyncio
import datetime
import sys
from pathlib import Path

import notifiers
from loguru import logger

from rivals_workshop_assistant.aseprite_handling.aseprite_updating import update_anims
from rivals_workshop_assistant.filelock import FileLock
from rivals_workshop_assistant import (
    updating,
    dotfile_mod,
    paths,
)
from rivals_workshop_assistant.dotfile_mod import (
    update_dotfile_after_saving,
)
from rivals_workshop_assistant.modes import Mode
from rivals_workshop_assistant.paths import LOGS_FOLDER, ASSISTANT_FOLDER
from rivals_workshop_assistant.run_context import (
    make_run_context_from_paths,
)
from rivals_workshop_assistant.script_handling.script_mod import (
    read_scripts,
    read_user_inject,
    read_lib_inject,
)
from rivals_workshop_assistant.script_handling.script_updating import update_scripts
from rivals_workshop_assistant.aseprite_handling.aseprites import (
    read_aseprites,
)
from rivals_workshop_assistant.asset_handling import get_required_assets, save_assets
from rivals_workshop_assistant.setup import (
    make_basic_folder_structure,
    get_assistant_folder_exists,
)
from rivals_workshop_assistant.script_handling.injection import (
    freshen_scripts_that_have_modified_dependencies,
)

__version__ = "1.2.27"

log_lines = []
has_encountered_error = False


def run_as_file():
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
        run_main_asyncio(exe_dir=exe_dir, project_dir=project_dir, mode=mode)
    except Exception as e:
        # This may be no longer needed because of @logger.catch
        import traceback

        print(e)
        print("".join(traceback.format_tb(e.__traceback__)))
    finally:
        if has_encountered_error:
            log = "".join(log_lines)

            try:
                from rivals_workshop_assistant.secrets import SLACK_WEBHOOK

                notifiers.notify(
                    "slack",
                    webhook_url=SLACK_WEBHOOK,
                    message=__version__,
                    attachments=[{"title": "log", "text": log, "fallback": log}],
                )
            except ImportError:
                logger.warning("Secrets file not present or malformed")


@logger.catch
def run_main_asyncio(
    exe_dir: Path,
    project_dir: Path,
    guarantee_root_dir: bool = False,
    mode: Mode = Mode.ALL,
):
    asyncio.run(
        main(
            exe_dir=exe_dir,
            given_dir=project_dir,
            guarantee_root_dir=guarantee_root_dir,
            mode=mode,
        )
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
    log_startup_context(exe_dir=exe_dir, root_dir=root_dir, mode=mode)

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


def do_first_run():
    print(
        """\
FIRST TIME SETUP
An `assistant` folder should have been created for you.
Stopping now so you have a chance to edit `assistant/assistant_config.yaml`.
Next time, the assistant will run normally. 
"""
    )


def log_startup_context(exe_dir: Path, root_dir: Path, mode: Mode):
    version_message = f"Assistant Version: {__version__}"
    logger.info(version_message)
    print(version_message)  # So that it always displays in the editor console.
    logger.info(f"Exe dir: {exe_dir}")
    logger.info(f"Root dir: {root_dir}")
    logger.info(f"Mode: {mode.name}")


async def update_files(exe_dir: Path, root_dir: Path, mode: Mode.ALL):
    run_context = await make_run_context_from_paths(exe_dir=exe_dir, root_dir=root_dir)

    await updating.update(run_context)

    scripts = read_scripts(run_context)

    user_inject_scripts = read_user_inject(run_context)
    lib_inject_scripts = read_lib_inject(run_context)

    freshen_scripts_that_have_modified_dependencies(
        run_context.dotfile,
        scripts=scripts,
        inject_scripts=user_inject_scripts + lib_inject_scripts,
    )

    aseprites = read_aseprites(run_context)
    if mode in (mode.ALL, mode.SCRIPTS):
        update_scripts(
            run_context=run_context,
            scripts=scripts,
            aseprites=aseprites,
        )

    if mode in (mode.ALL, mode.ANIMS):
        await update_anims(
            run_context=run_context,
            scripts=scripts,
            aseprites=aseprites,
        )

    update_dotfile_after_saving(
        now=datetime.datetime.now(), dotfile=run_context.dotfile, mode=mode
    )

    assets = get_required_assets(scripts)
    await save_assets(run_context.root_dir, assets)

    dotfile_mod.save_dotfile(run_context)


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


def set_encountered_error():
    global has_encountered_error
    has_encountered_error = True


def setup_logger(root_dir: Path):
    logger.add(
        root_dir / ASSISTANT_FOLDER / LOGS_FOLDER / f"assistant_{{time}}.log",
        retention="2 days",
        backtrace=True,
        diagnose=True,
    )
    logger.add(sys.stdout, level="WARNING")
    logger.add(lambda message: log_lines.append(message))
    logger.add(lambda _: set_encountered_error(), level="ERROR")


if __name__ == "__main__":
    run_as_file()
