import datetime
from pathlib import Path

import pytest
from testfixtures import TempDirectory

import rivals_workshop_assistant.assistant_config_mod
import rivals_workshop_assistant.dotfile_mod
import rivals_workshop_assistant.paths
import rivals_workshop_assistant.updating
from rivals_workshop_assistant.dotfile_mod import (
    LIBRARY_VERSION_FIELD,
)
from tests.testing_helpers import (
    create_script,
    ScriptWithPath,
    make_release,
    assert_script_with_path,
)

pytestmark = pytest.mark.slow


def test__get_releases():
    result = rivals_workshop_assistant.updating.get_library_releases()

    assert len(result) > 0 and isinstance(
        result[0], rivals_workshop_assistant.updating.Release
    )
    # Not going to mock it out, just make sure we get
    #   something


TEST_RELEASE = make_release(
    "0.0.0",
    "https://github.com/Rivals-Workshop-Community-Projects"
    "/injector-library/archive/0.0.0.zip",
)


def test__delete_old_release():
    with TempDirectory() as tmp:
        create_script(
            tmp,
            ScriptWithPath(
                path=rivals_workshop_assistant.paths.INJECT_FOLDER / "test.gml",
                content="test content",
            ),
        )

        rivals_workshop_assistant.updating._delete_old_library_release(Path(tmp.path))

        tmp.compare(
            path=rivals_workshop_assistant.paths.INJECT_FOLDER.as_posix(), expected=()
        )


def test__delete_old_release__none_exists():
    with TempDirectory() as tmp:
        rivals_workshop_assistant.updating._delete_old_library_release(Path(tmp.path))

        tmp.compare(
            path=rivals_workshop_assistant.paths.INJECT_FOLDER.as_posix(), expected=()
        )


def assert_test_release_scripts_installed(tmp):
    file_contents = tmp.read(
        (rivals_workshop_assistant.paths.INJECT_FOLDER / "logging.gml").as_posix(),
        encoding="utf8",
    )
    assert (
        file_contents
        == """\
#define prints()
    // Prints each parameter to console, separated by spaces.
    var _out_string = argument[0]
    for var i = 1; i < argument_count; i++ {
        _out_string += " "
        _out_string += string(argument[i])
    }
    print(_out_string)"""
    )


def test__download_and_unzip_release():
    with TempDirectory() as tmp:
        rivals_workshop_assistant.updating._download_and_unzip_library_release(
            root_dir=Path(tmp.path), release=TEST_RELEASE
        )
        assert_test_release_scripts_installed(tmp)


def test__install_release():
    with TempDirectory() as tmp:
        create_script(
            tmp,
            ScriptWithPath(
                path=rivals_workshop_assistant.dotfile_mod.PATH,
                content=f"{LIBRARY_VERSION_FIELD}: 0.0.0",
            ),
        )
        create_script(
            tmp,
            ScriptWithPath(
                path=rivals_workshop_assistant.assistant_config_mod.PATH,
                content="update_level: none",
            ),
        )
        create_script(
            tmp,
            ScriptWithPath(
                path=rivals_workshop_assistant.paths.INJECT_FOLDER / "test.gml",
                content="test content",
            ),
        )
        existing_user_inject = ScriptWithPath(
            path=rivals_workshop_assistant.paths.USER_INJECT_FOLDER / "users.gml",
            content="whatever",
        )
        create_script(tmp, existing_user_inject)

        rivals_workshop_assistant.updating.install_library_release(
            root_dir=Path(tmp.path), release=TEST_RELEASE
        )
        assert_test_release_scripts_installed(tmp)
        assert_script_with_path(tmp, existing_user_inject)
