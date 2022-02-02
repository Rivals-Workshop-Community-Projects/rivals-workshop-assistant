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
    assert "#define prints()" in file_contents
    # Hopefully asserts well formed content, while being flexible


def test__download_and_unzip_release():
    with TempDirectory() as tmp:
        rivals_workshop_assistant.updating._download_and_unzip_library_release(
            root_dir=Path(tmp.path), release=TEST_RELEASE
        )
        assert_test_release_scripts_installed(tmp)


@pytest.mark.asyncio
async def test__install_release():
    with TempDirectory() as root_dir, TempDirectory() as exe_dir:
        create_script(
            root_dir,
            ScriptWithPath(
                path=rivals_workshop_assistant.dotfile_mod.PATH,
                content=f"{LIBRARY_VERSION_FIELD}: 0.0.0",
            ),
        )
        create_script(
            root_dir,
            ScriptWithPath(
                path=rivals_workshop_assistant.assistant_config_mod.PATH,
                content="update_level: none",
            ),
        )
        create_script(
            root_dir,
            ScriptWithPath(
                path=rivals_workshop_assistant.paths.INJECT_FOLDER / "test.gml",
                content="test content",
            ),
        )
        existing_user_inject = ScriptWithPath(
            path=rivals_workshop_assistant.paths.USER_INJECT_FOLDER / "users.gml",
            content="whatever",
        )
        create_script(root_dir, existing_user_inject)

        await rivals_workshop_assistant.updating.update(
            exe_dir=Path(exe_dir.path),
            root_dir=Path(root_dir.path),
            dotfile={},
            config={},
        )
        assert_test_release_scripts_installed(root_dir)
        assert_script_with_path(root_dir, existing_user_inject)
