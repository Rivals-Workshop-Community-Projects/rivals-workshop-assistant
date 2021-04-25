import functools
import os
import subprocess
from pathlib import Path
from datetime import datetime

from rivals_workshop_assistant import paths
from rivals_workshop_assistant import aseprite_loading


def _get_is_fresh(processed_time: datetime, modified_time: datetime):
    if processed_time is None:
        return True
    return processed_time < modified_time


class File:
    def __init__(
        self,
        path: Path,
        modified_time: datetime,
        processed_time: datetime = None,
    ):
        self.path = path
        self.is_fresh = _get_is_fresh(processed_time, modified_time)


class Script(File):
    def __init__(
        self,
        path: Path,
        modified_time: datetime,
        original_content: str,
        working_content: str = None,
        processed_time: datetime = None,
    ):
        super().__init__(path, modified_time, processed_time)
        self.original_content = original_content

        if working_content is None:
            working_content = original_content
        self.working_content = working_content

    def save(self, root_dir: Path):
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


class Anim(File):
    def __init__(
        self,
        path: Path,
        modified_time: datetime,
        processed_time: datetime = None,
    ):
        super().__init__(path, modified_time, processed_time)

    @functools.cached_property
    def content(self):
        with open(self.path, "rb") as f:
            contents = f.read()
        return aseprite_loading.AsepriteFile(contents)

    @property
    def name(self):
        return self.path.stem

    @functools.cache
    def get_sprite_base_name(self, root_dir):
        relative_path = self.path.relative_to(root_dir / paths.ANIMS_FOLDER)
        subfolders = list(relative_path.parents)[:-1]
        path_parts = [path.name for path in reversed(subfolders)] + [self.name]
        base_name = "_".join(path_parts)
        return base_name

    def save(self, root_dir: Path, aseprite_path: Path, has_small_sprites: bool):
        self._delete_old_save(root_dir)

        num_frames = len(self.content.frames)
        dest_name = f"{self.get_sprite_base_name(root_dir)}_strip{num_frames}.png"
        dest = root_dir / paths.SPRITES_FOLDER / dest_name

        dest.parent.mkdir(parents=True, exist_ok=True)
        export_command = " ".join(
            [
                f'"{aseprite_path}"',
                "-b",
                f'"{self.path}"',
                f"--scale {int(has_small_sprites) + 1}",
                f'--sheet "{dest}"',
            ]
        )
        subprocess.run(export_command)

    def _delete_old_save(self, root_dir: Path):
        old_paths = (root_dir / paths.SPRITES_FOLDER).glob(
            f"{self.get_sprite_base_name(root_dir)}_strip*.png"
        )
        for old_path in old_paths:
            os.remove(old_path)
