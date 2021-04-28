import typing


TagColor = typing.Union[str, tuple[int, int, int]]


class AsepriteTag:
    def __init__(self, name: str, start: int, end: int, color: TagColor):
        self.name = name
        self.start = start
        self.end = end
        self.color = color
