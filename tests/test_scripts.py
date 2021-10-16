import rivals_workshop_assistant.dotfile_mod
import rivals_workshop_assistant.file_handling
from tests.testing_helpers import (
    PATH_ABSOLUTE,
    make_time,
    make_script,
    TEST_LATER_DATETIME_STRING,
)


def test_get_processed_time__no_register__none():
    dotfile = {}
    result = rivals_workshop_assistant.dotfile_mod.get_processed_time(
        dotfile=dotfile, path=PATH_ABSOLUTE
    )
    assert result is None


def test_get_processed_time():
    dotfile = {
        rivals_workshop_assistant.dotfile_mod.SEEN_FILES_FIELD: [
            PATH_ABSOLUTE.as_posix()
        ],
        rivals_workshop_assistant.dotfile_mod.PROCESSED_TIME_FIELD: make_time(),
    }

    result = rivals_workshop_assistant.dotfile_mod.get_processed_time(
        dotfile=dotfile, path=PATH_ABSOLUTE
    )

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

    rivals_workshop_assistant.dotfile_mod.update_dotfile_after_saving(
        dotfile=dotfile, now=time, seen_files=[script]
    )

    assert dotfile == {
        rivals_workshop_assistant.dotfile_mod.SEEN_FILES_FIELD: [
            script.path.as_posix()
        ],
        rivals_workshop_assistant.dotfile_mod.PROCESSED_TIME_FIELD: time,
    }
