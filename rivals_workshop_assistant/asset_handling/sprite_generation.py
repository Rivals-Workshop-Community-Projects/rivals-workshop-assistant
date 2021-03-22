import typing
from pathlib import Path

from PIL import Image, ImageDraw


def make_sprite_for_file_name(path: Path, file_name: str):
    """Controller"""
    raise NotImplementedError


def generate_sprite_for_file_name(file_name: str) -> ImageDraw:
    # colored_circle_pattern = "{:l}_circle_{:d}.png"
    # r = parse(, "The knights who say Ni!")

    file_name_parts = file_name.rstrip('.png').split('_')

    try:
        possible_name_locations = file_name_parts[:2]
        if 'circle' in possible_name_locations:
            *color, name, diameter = file_name_parts
            color = _get_color(color)
            height = diameter
            width = diameter

        elif ('ellipse' in possible_name_locations
              or 'rect' in possible_name_locations):
            *color, name, width, height = file_name_parts
            color = _get_color(color)
        else:
            return None

        width = int(width)
        height = int(height)
        sprite = make_canvas(int(width), int(height))

        if 'rect' in file_name_parts:
            get_drawable(sprite).rectangle((0, 0, width - 1, height - 1),
                                           fill=color,
                                           outline="black")
        else:
            get_drawable(sprite).ellipse((0, 0, width - 1, height - 1),
                                         fill=color,
                                         outline="black")

        return sprite
    except ValueError:
        return None


def _get_color(color_items: list) -> typing.Optional[str]:
    if len(color_items) == 0:
        return None
    elif len(color_items) == 1:
        return color_items[0]
    else:
        raise ValueError


def make_canvas(width, height):
    return Image.new('RGBA', (width, height))


def get_drawable(image):
    return ImageDraw.Draw(image)
