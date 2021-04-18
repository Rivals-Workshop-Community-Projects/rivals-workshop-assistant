import datetime
from pathlib import Path

from rivals_workshop_assistant.dotfile_mod import DotfileFields
from rivals_workshop_assistant import main as src

ROOT_PATH = Path("C:/a/file/path/the_root/")
PATH_ABSOLUTE = Path("C:/a/file/path/the_root/scripts/script_1.gml")
PATH_RELATIVE = Path("scripts/script_1.gml")
TEST_DATETIME = "2019-12-04*09:34:22"


def make_time(time_str=TEST_DATETIME):
    return datetime.datetime.fromisoformat(time_str)


def test_get_processed_time__no_register__none():
    processed_time_register = {}
    result = src.get_processed_time(processed_time_register, PATH_ABSOLUTE)
    assert result is None


def test_get_processed_time():
    processed_time_register = {PATH_ABSOLUTE: make_time()}
    result = src.get_processed_time(processed_time_register, PATH_ABSOLUTE)
    assert result == make_time()


def test_get_processed_time_register_logic():
    dotfile = {
        "unrelated": "Blah",
        DotfileFields.PROCESSED_TIME_REGISTER: {PATH_ABSOLUTE: make_time()},
    }
    result = src._get_processed_time_register_logic(ROOT_PATH, dotfile)

    assert result == {PATH_RELATIVE: make_time()}
