# noinspection PyPackageRequirements
from backports.cached_property import cached_property
from pathlib import Path
from datetime import datetime
from typing import List

from loguru import logger

from rivals_workshop_assistant.file_handling import (
    File,
    _get_modified_time,
)
from rivals_workshop_assistant.dotfile_mod import get_script_processed_time

from rivals_workshop_assistant.paths import (
    SCRIPTS_FOLDER,
    INJECT_FOLDER,
    USER_INJECT_FOLDER,
)
from rivals_workshop_assistant.run_context import RunContext


class Script(File):
    def __init__(
        self,
        path: Path,
        modified_time: datetime,
        original_content: str = None,
        working_content: str = None,
        processed_time: datetime = None,
    ):
        super().__init__(path, modified_time, processed_time)
        self._original_content = original_content
        self.working_content = working_content

    @cached_property
    def original_content(self):
        if self._original_content is None:
            self._original_content = self.path.read_text(
                encoding="UTF8", errors="surrogateescape"
            )
        return self._original_content

    @property
    def working_content(self):
        if self._working_content is None:
            self._working_content = self.original_content
        return self._working_content

    @working_content.setter
    def working_content(self, value):
        self._working_content = value

    def save(self, root_dir: Path):
        if self.working_content == "":
            logger.warning(f"Trying to save an empty file {self.path}")
            return
        if self.working_content != self.original_content:
            with open(
                (root_dir / self.path),
                "w",
                encoding="UTF8",
                errors="surrogateescape",
                newline="\n",
            ) as f:
                f.write(self.working_content)

    def __eq__(self, other: "Script"):
        return (
            self.path == other.path
            and self.original_content == other.original_content
            and self.working_content == other.working_content
            and self.is_fresh == other.is_fresh
        )

    def __str__(self):
        return self.path.name


def read_scripts(run_context: RunContext, folder: str = SCRIPTS_FOLDER) -> List[Script]:
    """Returns all Scripts in a given directory (defaults to the scripts folder)."""
    gml_paths = list((run_context.root_dir / folder).rglob("*.gml"))
    processed_time = get_script_processed_time(dotfile=run_context.dotfile)

    scripts = []
    for path in gml_paths:
        script = Script(
            path=path,
            modified_time=_get_modified_time(path),
            processed_time=processed_time,
        )
        scripts.append(script)

    return scripts


def read_user_inject(run_context: RunContext) -> List[Script]:
    """Returns all Scripts in the user_inject directory."""
    return read_scripts(run_context, folder=USER_INJECT_FOLDER)


def read_lib_inject(run_context: RunContext) -> List[Script]:
    """Returns all Scripts in the .inject directory."""
    return read_scripts(run_context, folder=INJECT_FOLDER)


def save_scripts(root_dir: Path, scripts: List["Script"]):
    for script in scripts:
        script.save(root_dir)
