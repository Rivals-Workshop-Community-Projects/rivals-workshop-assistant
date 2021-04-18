import datetime
from pathlib import Path

from rivals_workshop_assistant import main as src

PATH_ABSOLUTE = Path("C:/a/file/path/the_root/scripts/script_1.gml")
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
