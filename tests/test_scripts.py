import rivals_workshop_assistant.dotfile_mod as dotfile_mod
from rivals_workshop_assistant import main as src
from tests.testing_helpers import PATH_ABSOLUTE, make_time


def test_get_processed_time__no_register__none():
    dotfile = {}
    result = src.get_processed_time(dotfile=dotfile, path=PATH_ABSOLUTE)
    assert result is None


def test_get_processed_time():
    dotfile = {
        dotfile_mod.SEEN_FILES: [PATH_ABSOLUTE],
        dotfile_mod.PROCESSED_TIME: make_time(),
    }
    result = src.get_processed_time(dotfile=dotfile, path=PATH_ABSOLUTE)
    assert result == make_time()
