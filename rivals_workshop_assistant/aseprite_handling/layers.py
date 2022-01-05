from collections import defaultdict
from typing import List
from rivals_workshop_assistant.aseprite_handling import RawAsepriteFile

SPLIT = "SPLIT"
HURTBOX = "HURTBOX"
HURTMASK = "HURTMASK"


class AsepriteLayers:
    """Groups types of layers in assistant aseprite files"""

    def __init__(self, normals: List = None, hurtbox=None, hurtmask=None, splits=None):
        if normals is None:
            normals = []
        self.normals = normals

        self.hurtbox = hurtbox
        self.hurtmask = hurtmask

        if splits is None:
            splits = []
        self.splits = splits

    @classmethod
    def from_file(cls, file_data: RawAsepriteFile):
        normals = []
        hurtbox = None
        hurtmask = None
        splits = defaultdict(list)

        for layer in file_data.layers:
            name: str = layer.name
            if name.startswith(f"{SPLIT}("):
                split_name = name.split(f"{SPLIT}(")[1].split(")")[0]
                splits[split_name].append(layer)
            elif name == HURTBOX:
                hurtbox = layer
            elif name == HURTMASK:
                hurtmask = layer
            # todo add optional and either here as elifs
            else:
                normals.append(layer)
        return cls(normals=normals, hurtbox=hurtbox, hurtmask=hurtmask, splits=splits)
