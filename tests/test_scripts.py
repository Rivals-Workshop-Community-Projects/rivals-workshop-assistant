import rivals_workshop_assistant.dotfile_mod
import rivals_workshop_assistant.info_files as dotfile_mod
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
        rivals_workshop_assistant.dotfile_mod.SEEN_FILES_FIELD: [PATH_ABSOLUTE],
        rivals_workshop_assistant.dotfile_mod.PROCESSED_TIME_FIELD: make_time(),
    }
    result = src.get_processed_time(dotfile=dotfile, path=PATH_ABSOLUTE)
    assert result == make_time()


def test_dotfile_after_saving():
    dotfile = {
        rivals_workshop_assistant.dotfile_mod.SEEN_FILES_FIELD: ["some/other/path.gml"],
        rivals_workshop_assistant.dotfile_mod.PROCESSED_TIME_FIELD: make_time(
            TEST_LATER_DATETIME_STRING
        ),
    }

    script = make_script(PATH_ABSOLUTE, "content")
    time = make_time()

    src.update_dotfile_after_saving(dotfile=dotfile, now=time, files=[script])

    assert dotfile == {
        rivals_workshop_assistant.dotfile_mod.SEEN_FILES_FIELD: [
            script.path.as_posix()
        ],
        rivals_workshop_assistant.dotfile_mod.PROCESSED_TIME_FIELD: time,
    }
