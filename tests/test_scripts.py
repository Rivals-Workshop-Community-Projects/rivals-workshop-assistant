import rivals_workshop_assistant.dotfile_mod
import rivals_workshop_assistant.file_handling
from rivals_workshop_assistant.modes import Mode
from tests.testing_helpers import (
    PATH_ABSOLUTE,
    make_time,
    make_script,
    TEST_LATER_DATETIME_STRING,
)


def test_get_processed_time__no_register__none():
    dotfile = {}
    result = rivals_workshop_assistant.dotfile_mod.get_script_processed_time(
        dotfile=dotfile
    )
    assert result is None


def test_get_processed_time():
    dotfile = {
        rivals_workshop_assistant.dotfile_mod.SCRIPT_PROCESSED_TIME_FIELD: make_time(),
        rivals_workshop_assistant.dotfile_mod.ANIM_PROCESSED_TIME_FIELD: make_time(),
    }

    script_result = rivals_workshop_assistant.dotfile_mod.get_script_processed_time(
        dotfile=dotfile
    )
    anim_result = rivals_workshop_assistant.dotfile_mod.get_anim_processed_time(
        dotfile=dotfile
    )

    assert script_result == make_time()
    assert anim_result == make_time()


def test_dotfile_after_saving():
    dotfile = {
        rivals_workshop_assistant.dotfile_mod.SCRIPT_PROCESSED_TIME_FIELD: make_time(
            TEST_LATER_DATETIME_STRING
        ),
    }

    time = make_time()

    rivals_workshop_assistant.dotfile_mod.update_dotfile_after_saving(
        dotfile=dotfile, now=time, mode=Mode.SCRIPTS
    )

    assert dotfile == {
        rivals_workshop_assistant.dotfile_mod.SCRIPT_PROCESSED_TIME_FIELD: time,
    }
