import typing
from datetime import datetime
from pathlib import Path

import rivals_workshop_assistant.info_files as info_files
from rivals_workshop_assistant.modes import Mode
from rivals_workshop_assistant.paths import ASSISTANT_FOLDER

if typing.TYPE_CHECKING:
    from rivals_workshop_assistant.script_mod import Script
    from rivals_workshop_assistant.injection.dependency_handling import GmlInjection


FILENAME = ".assistant"
PATH = ASSISTANT_FOLDER / FILENAME

LIBRARY_VERSION_FIELD = "library_version"


def get_library_version_string(dotfile: dict) -> typing.Optional[str]:
    return dotfile.get(LIBRARY_VERSION_FIELD, None)


ASSISTANT_VERSION_FIELD = "assistant_version"


def get_assistant_version_string(dotfile: dict) -> typing.Optional[str]:
    return dotfile.get(ASSISTANT_VERSION_FIELD, None)


LAST_UPDATED_FIELD = "last_updated"
SCRIPT_PROCESSED_TIME_FIELD = "script_processed_time"
ANIM_PROCESSED_TIME_FIELD = "anim_processed_time"
INJECT_CLIENTS_FIELD = "injection_clients"


async def read(root_dir: Path) -> dict:
    """Controller"""
    return info_files.read(root_dir / PATH)


def save_dotfile(root_dir: Path, content: dict):
    """Controller"""
    info_files.save(path=root_dir / PATH, content=content)


def update_dotfile_after_saving(dotfile: dict, now: datetime, mode: Mode):
    if mode in (Mode.ALL, Mode.SCRIPTS):
        dotfile[SCRIPT_PROCESSED_TIME_FIELD] = now
    if mode in (Mode.ALL, Mode.ANIMS):
        dotfile[ANIM_PROCESSED_TIME_FIELD] = now


def update_all_dotfile_injection_clients(
    dotfile: dict,
    needed_injects: typing.List["GmlInjection"],
    script: "Script",
):
    if dotfile is not None:
        inject_scripts = []
        for injection in needed_injects:
            if not (injection.filepath is None or injection.filepath in inject_scripts):
                inject_scripts.append(injection.filepath)

        update_dotfile_injection_clients(
            dotfile=dotfile, client_script=script.path, dependencies=inject_scripts
        )


def update_dotfile_injection_clients(
    dotfile: dict, client_script: Path, dependencies: typing.List[Path]
):
    if INJECT_CLIENTS_FIELD not in dotfile:
        dotfile[INJECT_CLIENTS_FIELD] = {}

    if len(dependencies) > 0:
        dotfile[INJECT_CLIENTS_FIELD][client_script.as_posix()] = [
            dep.as_posix() for dep in dependencies
        ]
    elif client_script.as_posix() in dotfile[INJECT_CLIENTS_FIELD]:
        dotfile[INJECT_CLIENTS_FIELD].pop(client_script.as_posix())


def get_clients_for_injection(
    dotfile: dict, injection_script: Path
) -> typing.List[Path]:
    if INJECT_CLIENTS_FIELD not in dotfile:
        return []

    path_string = injection_script.as_posix()
    clients = []
    for key in dotfile[INJECT_CLIENTS_FIELD].keys():
        if path_string in dotfile[INJECT_CLIENTS_FIELD][key]:
            clients.append(Path(key))
    return clients


def get_script_processed_time(dotfile: dict) -> typing.Optional[datetime]:
    return dotfile.get(SCRIPT_PROCESSED_TIME_FIELD, None)


def get_anim_processed_time(dotfile: dict) -> typing.Optional[datetime]:
    return dotfile.get(ANIM_PROCESSED_TIME_FIELD, None)
