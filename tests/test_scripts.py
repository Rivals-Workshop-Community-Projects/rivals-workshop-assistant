import rivals_workshop_assistant.dotfile_mod as dotfile_mod
from rivals_workshop_assistant import main as src
from tests.testing_helpers import (
    PATH_ABSOLUTE,
    make_time,
    make_script,
    TEST_LATER_DATETIME_STRING,
)


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


def test_dotfile_after_saving():
    old_dotfile = {
        dotfile_mod.SEEN_FILES: ["some/other/path.gml"],
        dotfile_mod.PROCESSED_TIME: make_time(TEST_LATER_DATETIME_STRING),
    }

    script = make_script(PATH_ABSOLUTE, "content")
    time = make_time()

    result = src._update_docfile_after_saving_scripts(
        dotfile=old_dotfile, now=time, scripts=[script]
    )

    assert result == {
        dotfile_mod.SEEN_FILES: [script.path.as_posix()],
        dotfile_mod.PROCESSED_TIME: time,
    }
