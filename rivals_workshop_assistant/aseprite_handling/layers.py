from collections import defaultdict
from typing import List

from rivals_workshop_assistant.aseprite_handling import LayerChunk
from rivals_workshop_assistant.aseprite_handling._aseprite_loading import (
    RawAsepriteFile,
)

SPLIT = "SPLIT"
OPT = "OPT"
HURTBOX = "HURTBOX"
HURTMASK = "HURTMASK"

NORMAL_LAYER_TYPE = 0
GROUP_LAYER_TYPE = 1


def aseprite_layer_is_visible(layer: LayerChunk) -> bool:
    #  See visibility flag
    #  https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md#layer-chunk-0x2004
    return layer.flags % 2 == 1


class AsepriteLayers:
    """Groups types of layers in assistant aseprite files"""

    def __init__(
        self, normals: List = None, hurtbox=None, hurtmask=None, splits=None, opts=None
    ):
        if normals is None:
            normals = []
        self.normals = normals

        self.hurtbox = hurtbox
        self.hurtmask = hurtmask

        if splits is None:
            splits = []
        self.splits = splits
        if opts is None:
            opts = []
        self.opts = opts

    @classmethod
    def from_file(cls, file_data: RawAsepriteFile):
        normals = []
        hurtbox = None
        hurtmask = None
        splits = defaultdict(list)
        opts = defaultdict(list)

        layers = [
            layer for layer in file_data.layers if layer.layer_type == NORMAL_LAYER_TYPE
        ]
        for (i, layer) in enumerate(layers):
            layer.layer_index = i  # remove the layer groups from the ordering.

        layers = [layer for layer in layers if aseprite_layer_is_visible(layer)]

        # layer_groups = [
        # layer for layer in file_data.layers if layer.layer_type == GROUP_LAYER_TYPE
        # ]

        for layer in layers:
            name: str = layer.name
            if name.startswith(f"{SPLIT}("):
                split_name = name.split(f"{SPLIT}(")[1].split(")")[0]
                splits[split_name].append(layer)
            elif name.startswith(f"{OPT}("):
                opt_name = name.split(f"{OPT}(")[1].split(")")[0]
                opts[opt_name].append(layer)
            elif name == HURTBOX:
                hurtbox = layer
            elif name == HURTMASK:
                hurtmask = layer
            # todo add optional and either here as elifs
            else:
                normals.append(layer)
        return cls(
            normals=normals,
            hurtbox=hurtbox,
            hurtmask=hurtmask,
            splits=splits,
            opts=opts,
        )
