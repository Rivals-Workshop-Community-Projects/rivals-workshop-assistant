import asyncio
import itertools
from datetime import datetime
from pathlib import Path
from typing import List, TYPE_CHECKING

from rivals_workshop_assistant import assistant_config_mod
from rivals_workshop_assistant.aseprite_handling.anims import Anim
from rivals_workshop_assistant.aseprite_handling.windows import Window
from rivals_workshop_assistant.dotfile_mod import get_processed_time
from rivals_workshop_assistant.file_handling import File, _get_modified_time
from rivals_workshop_assistant.aseprite_handling._aseprite_loading import (
    RawAsepriteFile,
)
from rivals_workshop_assistant.aseprite_handling.layers import AsepriteLayers

if TYPE_CHECKING:
    from rivals_workshop_assistant.aseprite_handling.tags import TagColor
    from rivals_workshop_assistant.aseprite_handling.params import (
        AsepritePathParams,
        AsepriteConfigParams,
    )


class AsepriteFileContent:
    """Data class for the contents of an aseprite file."""

    # TODO remove functions from this and put them on `class Aseprite`
    def __init__(
        self,
        name: str,
        anim_tag_colors: List["TagColor"],
        window_tag_colors: List["TagColor"],
        file_data: "RawAsepriteFile",
        is_fresh: bool = False,
        layers: "AsepriteLayers" = None,  # just so it can be mocked
    ):
        self.file_data = file_data
        self.anim_tag_colors = anim_tag_colors
        self.window_tag_colors = window_tag_colors
        self.is_fresh = is_fresh

        if layers is None and file_data is not None:
            self.layers = AsepriteLayers.from_file(self.file_data)

        self.anims = self.get_anims(name)

    @property
    def num_frames(self):
        return self.file_data.get_num_frames()

    @property
    def tags(self):
        return self.file_data.get_tags()

    @classmethod
    def from_path(
        cls,
        name: str,
        path: Path,
        anim_tag_colors: List["TagColor"],
        window_tag_colors: List["TagColor"],
        is_fresh: bool,
    ):
        with open(path, "rb") as f:
            contents = f.read()
            raw_aseprite_file = RawAsepriteFile(contents)
        return cls(
            name=name,
            file_data=raw_aseprite_file,
            anim_tag_colors=anim_tag_colors,
            window_tag_colors=window_tag_colors,
            is_fresh=is_fresh,
        )

    def get_anims(self, name):
        #     def _get_is_fresh(self):
        # frame_hashes = [ self._get_frame_hash(frame) for frame in ]
        #
        # def _get_frame_hash(self, frame):
        #     return hashlib.md5(pickle.dumps(self.content.file_data.frames[frame])).hexdigest()

        tag_anims = [
            self.make_anim(
                name=tag.name,
                start=tag.start,
                end=tag.end,
                is_fresh=self.is_fresh,
                content=self,
            )
            for tag in self.tags
            if tag.color in self.anim_tag_colors
        ]
        if tag_anims:
            return tag_anims
        else:
            return [
                self.make_anim(
                    name=name,
                    start=0,
                    end=self.num_frames - 1,
                    is_fresh=self.is_fresh,
                    content=self,
                )
            ]

    def make_anim(
        self,
        name: str,
        start: int,
        end: int,
        is_fresh: bool,
        content: "AsepriteFileContent",
    ):
        return Anim(
            name=name,
            start=start,
            end=end,
            windows=self.get_windows_in_frame_range(start=start, end=end),
            is_fresh=is_fresh,
            content=content,
        )

    def get_windows_in_frame_range(self, start: int, end: int):
        tags_in_frame_range = [
            window
            for window in self.tags
            if window.color in self.window_tag_colors
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
        anim_tag_colors: List["TagColor"],
        window_tag_colors: List["TagColor"],
        modified_time: datetime = None,
        processed_time: datetime = None,
        content=None,
        # anims: Anim = None,
    ):
        super().__init__(path, modified_time, processed_time)
        self.anim_tag_colors = anim_tag_colors
        self.window_tag_colors = window_tag_colors
        self._content = content
        # self._anims = anims

    @property
    def content(self) -> AsepriteFileContent:
        if self._content is None:
            self._content = AsepriteFileContent.from_path(
                name=self.name,
                path=self.path,
                anim_tag_colors=self.anim_tag_colors,
                window_tag_colors=self.window_tag_colors,
                is_fresh=self.is_fresh,
            )
        return self._content

    @property
    def name(self):
        return self.path.stem

    # @property
    # def anims(self):
    #     if self._anims is None:
    #         self._anims = self.get_anims()
    #     return self._anims

    async def save(
        self,
        path_params: "AsepritePathParams",
        config_params: "AsepriteConfigParams",
    ):
        coroutines = []
        for anim in self.content.anims:
            coroutines.append(
                anim.save(path_params, config_params, aseprite_file_path=self.path)
            )
        await asyncio.gather(*coroutines)


def read_aseprites(
    root_dir: Path, dotfile: dict, assistant_config: dict
) -> List[Aseprite]:
    ase_paths = itertools.chain(
        *[
            list((root_dir / "anims").rglob(f"*.{filetype}"))
            for filetype in ("ase", "aseprite")
        ]
    )

    aseprites = []
    for path in ase_paths:
        aseprite = read_aseprite(path, dotfile, assistant_config)
        aseprites.append(aseprite)
    return aseprites


def read_aseprite(path: Path, dotfile: dict, assistant_config: dict) -> Aseprite:
    aseprite = Aseprite(
        path=path,
        modified_time=_get_modified_time(path),
        processed_time=get_processed_time(dotfile=dotfile, path=path),
        anim_tag_colors=assistant_config_mod.get_anim_tag_color(assistant_config),
        window_tag_colors=assistant_config_mod.get_window_tag_color(assistant_config),
    )
    return aseprite
