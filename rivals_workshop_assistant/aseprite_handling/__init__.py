import asyncio
import itertools
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from rivals_workshop_assistant import paths, assistant_config_mod
from ._aseprite_loading import RawAsepriteFile, LayerChunk
from .constants import (
    ANIMS_WHICH_CARE_ABOUT_SMALL_SPRITES,
    HURTMASK_LAYER_NAME,
    HURTBOX_LAYER_NAME,
    ANIMS_WHICH_GET_HURTBOXES,
)
from .layers import AsepriteLayers
from .lua_scripts import LUA_SCRIPTS
from ..file_handling import File, _get_modified_time, create_file
from ..dotfile_mod import get_processed_time
from .types import AsepriteTag, TagColor
from ..paths import ASEPRITE_LUA_SCRIPTS_FOLDER


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
#macro {self.name.upper()}_FRAMES {self.end - self.start + 1}
#define _get_{self.name}_frames()
    return {self.name.upper()}_FRAMES
#macro {self.name.upper()}_FRAME_START {self.start - 1}
#define _get_{self.name}_frame_start()
    return {self.name.upper()}_FRAME_START"""


def supply_lua_script(path: Path):
    script_name = path.stem
    script_content = LUA_SCRIPTS[script_name]
    create_file(path=path, content=script_content, overwrite=False)


@dataclass
class AsepritePathParams:
    exe_dir: Path
    root_dir: Path
    aseprite_program_path: Path


@dataclass
class AsepriteConfigParams:
    has_small_sprites: bool = False
    hurtboxes_enabled: bool = False
    is_ssl: bool = False


EXPORT_ASEPRITE_LUA_PATH = "export_aseprite.lua"
CREATE_HURTBOX_LUA_PATH = "create_hurtbox.lua"


class Anim(TagObject):
    def __init__(
        self,
        name: str,
        start: int,
        end: int,
        content: "AsepriteData",
        windows: List[Window] = None,
        is_fresh=False,
    ):
        """A part of an aseprite file representing a single spritesheet.
        An Aseprite file may contain multiple anims.
        """
        super().__init__(name, start, end)
        self.content = content
        if windows is None:
            windows = []
        self.windows = windows
        self.is_fresh = is_fresh

    @property
    def num_frames(self):
        return self.end - self.start + 1

    def __eq__(self, other):
        return self.name == other.name

    async def save(
        self,
        path_params: AsepritePathParams,
        config_params: AsepriteConfigParams,
        aseprite_file_path: Path,
    ):
        root_name = get_anim_file_name_root(
            path_params.root_dir, aseprite_file_path, self.name
        )
        if config_params.has_small_sprites and self._cares_about_small_sprites():
            scale_param = 1
        else:
            scale_param = 2
        if config_params.is_ssl:
            scale_param *= 2

        @dataclass
        class ExportLayerParams:
            name: str
            target_layers: List[LayerChunk]

        normal_run_params = [ExportLayerParams(root_name, self.content.layers.normals)]
        splits_run_params = [
            ExportLayerParams(f"{root_name}_{split_name}", layers)
            for split_name, layers in self.content.layers.splits.items()
        ]
        all_run_params = normal_run_params + splits_run_params

        coroutines = []

        for run_params in all_run_params:
            target_layers = _get_layer_indices(run_params.target_layers)
            coroutines.append(
                self._run_lua_export(
                    path_params=path_params,
                    aseprite_file_path=aseprite_file_path,
                    base_name=run_params.name,
                    script_name=EXPORT_ASEPRITE_LUA_PATH,
                    lua_params={
                        "scale": scale_param,
                        "targetLayers": target_layers,
                    },
                )
            )

            if config_params.hurtboxes_enabled and self._gets_a_hurtbox():
                coroutines.append(
                    self._run_lua_export(
                        path_params=path_params,
                        aseprite_file_path=aseprite_file_path,
                        base_name=f"{run_params.name}_hurt",
                        script_name=CREATE_HURTBOX_LUA_PATH,
                        lua_params={
                            "targetLayers": target_layers,
                            "hurtboxLayer": self.content.layers.hurtbox,
                            "hurtmaskLayer": self.content.layers.hurtmask,
                        },
                    )
                )
        await asyncio.gather(*coroutines)

    async def _run_lua_export(
        self,
        path_params: AsepritePathParams,
        aseprite_file_path: Path,
        base_name: str,
        script_name: str,
        lua_params: dict = None,
    ):
        full_script_path = (
            path_params.exe_dir / ASEPRITE_LUA_SCRIPTS_FOLDER / script_name
        ).absolute()
        supply_lua_script(
            path=full_script_path,
        )

        if lua_params is None:
            lua_params = {}

        _delete_paths_from_glob(
            path_params.root_dir,
            f"{base_name}_strip*.png",
        )

        dest_name = f"{base_name}_strip{self.num_frames}.png"
        dest = path_params.root_dir / paths.SPRITES_FOLDER / dest_name
        dest.parent.mkdir(parents=True, exist_ok=True)

        command_parts = (
            [
                f'"{path_params.aseprite_program_path}"',
                "-b",
                _format_param("filename", aseprite_file_path),
                _format_param("dest", dest),
                _format_param("startFrame", self.start + 1),
                _format_param("endFrame", self.end + 1),
            ]
            + [_format_param(key, value) for key, value in lua_params.items()]
            + [
                f'-script "{full_script_path}"',
            ]
        )
        export_command = " ".join(command_parts)
        print(f"Running lua script: {export_command}")
        try:
            result = subprocess.run(export_command)
            if result.returncode != 0:
                print(f"ERROR: Lua script command failed. {export_command}")
        except FileNotFoundError:
            print(f"ERROR: Aseprite not found at {path_params.aseprite_program_path}")
        except PermissionError as e:
            print(repr(e))

    def _cares_about_small_sprites(self):
        return self.name in ANIMS_WHICH_CARE_ABOUT_SMALL_SPRITES

    def _gets_a_hurtbox(self):
        return self.name in ANIMS_WHICH_GET_HURTBOXES


def _get_layer_indices(layers: List[LayerChunk]) -> List[int]:
    # change to 1-indexing
    return [layer.layer_index + 1 for layer in layers]


def _format_param(param_name, value):
    if isinstance(value, list):
        # Format list as `a,b,c` instead of `[a, b, c]` for easier parsing.
        value = ",".join(str(item) for item in value)
    return f'-script-param {param_name}="{value}"'


def _delete_paths_from_glob(root_dir: Path, paths_glob: str):
    """Delete paths matching the glob"""
    old_paths = (root_dir / paths.SPRITES_FOLDER).glob(paths_glob)
    for old_path in old_paths:
        os.remove(old_path)


def get_anim_file_name_root(root_dir: Path, aseprite_file_path: Path, name: str) -> str:
    """Return the anim's name, prefixed with any subfolders the anim is in.
    anims/vfx/hitfx/star.aseprite -> 'vfx_hitfx_star'"""
    try:
        relative_path = aseprite_file_path.relative_to(root_dir / paths.ANIMS_FOLDER)
    except ValueError:
        # The aseprite file path isn't in the root dir, maybe because testing.
        return name
    subfolders = list(relative_path.parents)[:-1]
    path_parts = [path.name for path in reversed(subfolders)] + [name]
    base_name = "_".join(path_parts)
    return base_name


class AsepriteData:
    def __init__(
        self,
        name: str,
        anim_tag_colors: List[TagColor],
        window_tag_colors: List[TagColor],
        file_data: RawAsepriteFile,
        is_fresh: bool = False,
        layers: AsepriteLayers = None,  # just so it can be mocked
    ):
        self.file_data = file_data
        self.anim_tag_colors = anim_tag_colors
        self.window_tag_colors = window_tag_colors
        self.is_fresh = is_fresh

        self.anims = self.get_anims(name)
        if layers is None and file_data is not None:
            self.layers = AsepriteLayers.from_file(self.file_data)

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
        anim_tag_colors: List[TagColor],
        window_tag_colors: List[TagColor],
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

    def get_anims(self, name: str):
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
        self, name: str, start: int, end: int, is_fresh: bool, content: "AsepriteData"
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
        anim_tag_colors: List[TagColor],
        window_tag_colors: List[TagColor],
        modified_time: datetime = None,
        processed_time: datetime = None,
        content=None,
    ):
        super().__init__(path, modified_time, processed_time)
        self.anim_tag_colors = anim_tag_colors
        self.window_tag_colors = window_tag_colors
        self._content = content

    @property
    def content(self) -> AsepriteData:
        if self._content is None:
            self._content = AsepriteData.from_path(
                name=self.path.stem,
                path=self.path,
                anim_tag_colors=self.anim_tag_colors,
                window_tag_colors=self.window_tag_colors,
                is_fresh=self.is_fresh,
            )
        return self._content

    @property
    def name(self):
        return self.path.stem

    async def save(
        self,
        path_params: AsepritePathParams,
        config_params: AsepriteConfigParams,
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


def get_anims(aseprites: List[Aseprite]) -> List[Anim]:
    return list(itertools.chain(*[aseprite.content.anims for aseprite in aseprites]))
    # Unfortunately this involves reading every aseprite file...
    # If we demand that multi-anim files have a name prefix,
    # we could get away with reading fewer files.


async def save_anims(
    path_params: AsepritePathParams,
    config_params: AsepriteConfigParams,
    aseprites: List[Aseprite],
):
    if not path_params.aseprite_program_path:
        print(
            "WARN: Not saving anims, because no aseprite path has been supplied.\n"
            "Add a path to your aseprite.exe in assistant/assistant_config.yaml to "
            "process aseprite files."
        )
        return
    coroutines = []
    for aseprite in aseprites:
        if aseprite.is_fresh:
            coroutines.append(
                aseprite.save(path_params=path_params, config_params=config_params)
            )
    await asyncio.gather(*coroutines)
