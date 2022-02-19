import asyncio
import hashlib
import itertools
import os
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List, TYPE_CHECKING, Dict

from loguru import logger

from rivals_workshop_assistant import paths
from rivals_workshop_assistant.aseprite_handling.windows import (
    Window,
)
from rivals_workshop_assistant.aseprite_handling._aseprite_loading.chunks import (
    LayerChunk,
)
from rivals_workshop_assistant.aseprite_handling.lua_scripts import (
    EXPORT_ASEPRITE_LUA_PATH,
    CREATE_HURTBOX_LUA_PATH,
    supply_lua_script,
)
from rivals_workshop_assistant.aseprite_handling.constants import (
    ANIMS_WHICH_CARE_ABOUT_SMALL_SPRITES,
    ANIMS_WHICH_GET_HURTBOXES,
)
from rivals_workshop_assistant.aseprite_handling.tag_objects import TagObject
from rivals_workshop_assistant.paths import ASEPRITE_LUA_SCRIPTS_FOLDER

if TYPE_CHECKING:
    from rivals_workshop_assistant.aseprite_handling.aseprites import (
        AsepriteFileContent,
        Aseprite,
    )
    from rivals_workshop_assistant.aseprite_handling.params import (
        AsepritePathParams,
        AsepriteConfigParams,
    )


class AnimHashes:
    def __init__(self, dotfile: dict):
        self.dict = dotfile.get("anim_hashes", {})


class Anim(TagObject):
    def __init__(
        self,
        name: str,
        start: int,
        end: int,
        content: "AsepriteFileContent",
        windows: List[Window] = None,
        file_is_fresh=False,
        anim_hashes: Dict[str, str] = None,
    ):
        """A part of an aseprite file representing a single spritesheet.
        An Aseprite file may contain multiple anims.
        """
        super().__init__(name, start, end)
        self.content = content
        if windows is None:
            windows = []
        if anim_hashes is None:
            anim_hashes = {}
        self.windows = windows
        self.anim_hashes = anim_hashes
        self.file_is_fresh = file_is_fresh

        self._frame_hash = self._get_frame_hash()
        self.is_fresh = self._get_is_fresh()
        self._save_hash()

    @property
    def num_frames(self):
        return self.end - self.start + 1

    def __get_keys(self):
        return self.name, self.start, self.end, self.windows, self.is_fresh

    def __eq__(self, other):
        if not isinstance(other, Anim):
            return NotImplemented
        return self.__get_keys() == other.__get_keys()

    def __hash__(self):
        return hash(self.__get_keys())

    async def save(
        self,
        path_params: "AsepritePathParams",
        config_params: "AsepriteConfigParams",
        aseprite_file_path: Path,
    ):
        root_name = get_anim_file_name_root(
            path_params.root_dir, aseprite_file_path, self.name.lower()
        )
        if config_params.has_small_sprites and self._cares_about_small_sprites():
            scale_param = 1
        else:
            scale_param = 2
        hurtbox_scale_param = 2
        if config_params.is_ssl:
            scale_param *= 2
            hurtbox_scale_param *= 2

        @dataclass
        class ExportLayerParams:
            name: str
            target_layers: List[LayerChunk]

        normal_run_params = [ExportLayerParams(root_name, self.content.layers.normals)]
        splits_run_params = [
            ExportLayerParams(f"{root_name}_{split_name}", split_layers)
            for split_name, split_layers in self.content.layers.splits.items()
        ]
        opts_run_params = [
            ExportLayerParams(
                f"{root_name}_{opt_name}", self.content.layers.normals + opt_layers
            )
            for opt_name, opt_layers in self.content.layers.opts.items()
        ]
        all_run_params = normal_run_params + splits_run_params + opts_run_params

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
                            "scale": hurtbox_scale_param,
                            "targetLayers": target_layers,
                            "hurtboxLayer": self.content.layers.hurtbox,
                            "hurtmaskLayer": self.content.layers.hurtmask,
                        },
                    )
                )
        await asyncio.gather(*coroutines)

    async def _run_lua_export(
        self,
        path_params: "AsepritePathParams",
        aseprite_file_path: Path,
        base_name: str,
        script_name: str,
        lua_params: dict = None,
    ):
        logger.info(
            f"Exporting anim {dict({'name': base_name, 'script': script_name})}"
        )
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
        logger.debug(f"Running lua script: {export_command}")
        try:
            proc = await asyncio.create_subprocess_shell(
                export_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if stdout:
                logger.debug(f"[stdout] {stdout}")
            if proc.returncode != 0:
                logger.error(f"Lua script command failed.")
                if stderr:
                    logger.error(f"[stderr] {stderr.decode()}")
            elif not aseprite_file_path.exists():
                logger.error(
                    f"Exported aseprite file {aseprite_file_path} not found, "
                    f"although no error from aseprite."
                )
        except FileNotFoundError:
            logger.error(f"Aseprite not found at {path_params.aseprite_program_path}")
        except PermissionError as e:
            logger.error(repr(e))

    def _cares_about_small_sprites(self):
        return self.name in ANIMS_WHICH_CARE_ABOUT_SMALL_SPRITES

    def _gets_a_hurtbox(self):
        return self.name in ANIMS_WHICH_GET_HURTBOXES

    def _get_is_fresh(self):
        if not self.file_is_fresh:
            return False

        last_frame_hash = self.anim_hashes.get(self.name, None)
        return self._frame_hash != last_frame_hash

    def _get_frame_hash(self):
        try:
            return hashlib.md5(
                pickle.dumps(self.content.file_data.frames[self.start : self.end + 1])
            ).hexdigest()
        except AttributeError:
            logger.error(
                f"Could not make checksum for {dict({'name': self.name, 'start': self.start, 'end': self.end})}"
            )
            return 0

    def _save_hash(self):
        self.anim_hashes[self.name] = self._frame_hash


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
        logger.error(
            f"Aseprite file path, isn't in the root dir. This is okay when testing, not in production. "
            f"{dict({'root_dir':root_dir, 'aseprite_file_path': aseprite_file_path})}"
        )
        return name
    subfolders = list(relative_path.parents)[:-1]
    path_parts = [path.name for path in reversed(subfolders)] + [name]
    base_name = "_".join(path_parts)
    return base_name


def get_anims(aseprites: List["Aseprite"]) -> List["Anim"]:
    return list(itertools.chain(*[aseprite.anims for aseprite in aseprites]))
    # Unfortunately this involves reading every aseprite file...
    # If we demand that multi-anim files have a name prefix,
    # we could get away with reading fewer files.


async def save_anims(
    path_params: "AsepritePathParams",
    config_params: "AsepriteConfigParams",
    aseprites: List["Aseprite"],
):
    if not path_params.aseprite_program_path:
        logger.warning(
            "Not saving anims, because no aseprite path has been supplied.\n"
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
