import functools
import os
import subprocess
from datetime import datetime
from pathlib import Path

from rivals_workshop_assistant import paths
from ._aseprite_loading import RawAsepriteFile
from rivals_workshop_assistant.script_mod import File
from .types import AsepriteTag


class Anim:
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name


class AsepriteData:
    def __init__(self, num_frames, tags: list[AsepriteTag] = None):
        self.num_frames = num_frames
        if tags is None:
            tags = []
        self.tags = tags
        self.anims = get_anims(tags)

    @classmethod
    def from_path(cls, path):
        with open(path, "rb") as f:
            contents = f.read()
            raw_aseprite_file = RawAsepriteFile(contents)
        tags = raw_aseprite_file.get_tags()
        num_frames = raw_aseprite_file.get_num_frames()
        return cls(tags=tags, num_frames=num_frames)


def get_anims(tags: list[AsepriteTag]):
    return [Anim(name=tag.name) for tag in tags]  # todo


class Aseprite(File):
    def __init__(
        self,
        path: Path,
        modified_time: datetime,
        processed_time: datetime = None,
        content=None,
    ):
        super().__init__(path, modified_time, processed_time)
        self._content = content

    @property
    def content(self) -> AsepriteData:
        if self._content is None:
            self._content = AsepriteData.from_path(self.path)
        return self._content

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

        dest_name = (
            f"{self.get_sprite_base_name(root_dir)}_strip{self.content.num_frames}.png"
        )
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
