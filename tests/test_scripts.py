import datetime
from pathlib import Path

import rivals_workshop_assistant.dotfile_mod as dotfile_mod
from rivals_workshop_assistant import main as src

ROOT_PATH = Path("C:/a/file/path/the_root/")
PATH_ABSOLUTE = Path("C:/a/file/path/the_root/scripts/script_1.gml")
PATH_RELATIVE = Path("scripts/script_1.gml")
TEST_DATETIME = "2019-12-04*09:34:22"


def make_time(time_str=TEST_DATETIME):
    return datetime.datetime.fromisoformat(time_str)


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
