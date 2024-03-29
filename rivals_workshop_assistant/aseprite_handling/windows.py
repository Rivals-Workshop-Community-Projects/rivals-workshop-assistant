from rivals_workshop_assistant.aseprite_handling.tag_objects import TagObject


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

    def __get_keys(self):
        return self.name, self.start, self.end, self.gml

    def __eq__(self, other):
        if not isinstance(other, Window):
            return NotImplemented
        return self.__get_keys() == other.__get_keys()

    def __hash__(self):
        return hash(self.__get_keys())
