import os
import subprocess
from datetime import datetime
from pathlib import Path

from rivals_workshop_assistant import paths
from ._aseprite_loading import RawAsepriteFile
from rivals_workshop_assistant.script_mod import File
from .types import AsepriteTag, TagColor


class TagObject:
    def __init__(self, name: str, start: int, end: int):
        self.name = name
        self.start = start
        self.end = end


class Window(TagObject):
    """An attack window in an anim.
    Start and end are relative to the anim, not the aseprite file."""

    def __init__(self, name: str, start: int, end: int):
        super().__init__(name, start, end)
        self.gml = self._make_gml()

    def _make_gml(self):
        return f"""\
#macro {self.name.upper()}_FRAMES {self.end-self.start + 1}
#macro {self.name.upper()}_FRAME_START {self.start}"""


class Anim(TagObject):
    def __init__(self, name: str, start: int, end: int, windows: list[Window] = None):
        """A part of an aseprite file representing a single spritesheet.
        An Aseprite file may contain multiple anims.
        """
        super().__init__(name, start, end)
        if windows is None:
            windows = []
        self.windows = windows

    @property
    def num_frames(self):
        return self.end - self.start + 1

    def __eq__(self, other):
        return self.name == other.name


class AsepriteData:
    def __init__(
        self,
        name: str,
        num_frames: int,
        anim_tag_color: TagColor,
        window_tag_color: TagColor,
        tags: list[AsepriteTag] = None,
    ):
        self.num_frames = num_frames
        if tags is None:
            tags = []
        self.tags = tags
        self.anim_tag_color = anim_tag_color
        self.window_tag_color = window_tag_color
        self.anims = self.get_anims(name)

    @classmethod
    def from_path(
        cls, name: str, path: Path, anim_tag_color: TagColor, window_tag_color: TagColor
    ):
        with open(path, "rb") as f:
            contents = f.read()
            raw_aseprite_file = RawAsepriteFile(contents)
        tags = raw_aseprite_file.get_tags()
        num_frames = raw_aseprite_file.get_num_frames()
        return cls(
            name=name,
            tags=tags,
            num_frames=num_frames,
            anim_tag_color=anim_tag_color,
            window_tag_color=window_tag_color,
        )

    def get_anims(self, name: str):
        tag_anims = [
            self.make_anim(name=tag.name, start=tag.start, end=tag.end)
            for tag in self.tags
            if tag.color == self.anim_tag_color
        ]
        if tag_anims:
            return tag_anims
        else:
            return [self.make_anim(name=name, start=0, end=self.num_frames - 1)]

    def make_anim(self, name: str, start: int, end: int):
        return Anim(
            name=name,
            start=start,
            end=end,
            windows=self.get_windows_in_frame_range(start=start, end=end),
        )

    def get_windows_in_frame_range(self, start: int, end: int):
        tags_in_frame_range = [
            window
            for window in self.tags
            if window.color == self.window_tag_color
            and start <= window.start <= end
            and start <= window.end <= end
        ]
        windows = [
            Window(name=tag.name, start=tag.start - start + 1, end=tag.end - start + 1)
            for tag in tags_in_frame_range
        ]
        return windows


class Aseprite(File):
    def __init__(
        self,
        path: Path,
        anim_tag_color: TagColor,
        window_tag_color: TagColor,
        modified_time: datetime,
        processed_time: datetime = None,
        content=None,
    ):
        super().__init__(path, modified_time, processed_time)
        self.anim_tag_color = anim_tag_color
        self.window_tag_color = window_tag_color
        self._content = content

    @property
    def content(self) -> AsepriteData:
        if self._content is None:
            self._content = AsepriteData.from_path(
                name=self.path.stem,
                path=self.path,
                anim_tag_color=self.anim_tag_color,
                window_tag_color=self.window_tag_color,
            )
        return self._content

    @property
    def name(self):
        return self.path.stem

    def save(self, root_dir: Path, aseprite_path: Path, has_small_sprites: bool):
        for anim in self.content.anims:
            self._save_anim(
                anim=anim,
                root_dir=root_dir,
                aseprite_path=aseprite_path,
                has_small_sprites=has_small_sprites,
            )

    def _save_anim(
        self, anim: Anim, root_dir: Path, aseprite_path: Path, has_small_sprites: bool
    ):
        self._delete_old_save(root_dir, anim.name)
        dest_name = (
            f"{self.get_anim_base_name(root_dir, anim.name)}"
            f"_strip{anim.num_frames}.png"
        )
        dest = root_dir / paths.SPRITES_FOLDER / dest_name

        dest.parent.mkdir(parents=True, exist_ok=True)

        command_parts = [
            f'"{aseprite_path}"',
            "-b",
            f"--frame-range {anim.start},{anim.end}",
            f'"{self.path}"',
            f"--scale {int(has_small_sprites) + 1}",
            f'--sheet "{dest}"',
        ]

        export_command = " ".join(command_parts)

        subprocess.run(export_command)

    def _delete_old_save(self, root_dir: Path, name: str):
        old_paths = (root_dir / paths.SPRITES_FOLDER).glob(
            f"{self.get_anim_base_name(root_dir, name)}_strip*.png"
        )
        for old_path in old_paths:
            os.remove(old_path)

    def get_anim_base_name(self, root_dir: Path, name: str):
        relative_path = self.path.relative_to(root_dir / paths.ANIMS_FOLDER)
        subfolders = list(relative_path.parents)[:-1]
        path_parts = [path.name for path in reversed(subfolders)] + [name]
        base_name = "_".join(path_parts)
        return base_name
