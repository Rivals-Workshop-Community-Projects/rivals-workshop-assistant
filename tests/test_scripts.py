from rivals_workshop_assistant import dotfile_mod
from rivals_workshop_assistant.file_handling import File
from rivals_workshop_assistant.modes import Mode
from tests.testing_helpers import (
    make_time,
    TEST_LATER_DATETIME_STRING,
    TEST_EARLIER_DATETIME_STRING,
    PATH_A,
)

from loguru import logger

logger.remove()


def test_get_processed_time__no_register__none():
    dotfile = {}
    result = dotfile_mod.get_script_processed_time(dotfile=dotfile)
    assert result is None


def test_get_processed_time():
    dotfile = {
        dotfile_mod.SCRIPT_PROCESSED_TIME_FIELD: make_time(),
        dotfile_mod.ANIM_PROCESSED_TIME_FIELD: make_time(),
    }

    script_result = dotfile_mod.get_script_processed_time(dotfile=dotfile)
    anim_result = dotfile_mod.get_anim_processed_time(dotfile=dotfile)

    assert script_result == make_time()
    assert anim_result == make_time()


def test_dotfile_after_saving():
    dotfile = {
        dotfile_mod.SCRIPT_PROCESSED_TIME_FIELD: make_time(TEST_LATER_DATETIME_STRING),
    }

    time = make_time()

    dotfile_mod.update_dotfile_after_saving(
        dotfile=dotfile, now=time, mode=Mode.SCRIPTS
    )

    assert dotfile == {
        dotfile_mod.SCRIPT_PROCESSED_TIME_FIELD: time,
    }


def file_not_modified_since_last_run_is_not_fresh():
    file = File(
        path=PATH_A,
        modified_time=make_time(TEST_EARLIER_DATETIME_STRING),
        processed_time=make_time(),
    )

    assert not file.is_fresh


def file_modified_since_last_run_is_fresh():
    file = File(
        path=PATH_A,
        modified_time=make_time(TEST_LATER_DATETIME_STRING),
        processed_time=make_time(),
    )

    assert file.is_fresh
