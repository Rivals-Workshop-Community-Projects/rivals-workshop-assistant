from pathlib import Path

import pytest
from testfixtures import TempDirectory

from rivals_workshop_assistant.injection.library import INJECT_FOLDER, \
    DOTFILE_PATH
from rivals_workshop_assistant.injection import installation as src
from tests.testing_helpers import make_script, ScriptWithPath

pytestmark = pytest.mark.slow


def test__get_update_config():
    with TempDirectory() as tmp:
        make_script(tmp, ScriptWithPath(
            path=INJECT_FOLDER / Path(src.INJECT_CONFIG_NAME),
            content=f"""\

{src.UPDATE_LEVEL_NAME}: minor

"""))

        result = src.get_update_config(Path(tmp.path))
        assert result == src.UpdateConfig.MINOR


def test__get_releases():
    result = src.get_releases()

    assert len(result) > 0 and type(result[0]) == src.Release
    # Not going to mock it out, just make sure we get
    #   something


def test__update_dotfile_with_new_release():
    with TempDirectory() as tmp:
        make_script(tmp, ScriptWithPath(
            path=DOTFILE_PATH,
            content="other_content: 42"
        ))

        src._update_dotfile_with_new_version(root_dir=Path(tmp.path),
                                             version=src.Version(major=4,
                                                                 minor=5,
                                                                 patch=6))
        result = tmp.read(DOTFILE_PATH.as_posix(), encoding='utf8')

        assert result == """\
other_content: 42
version: 4.5.6
"""


def test__update_dotfile_with_new_release_when_missing_dotfile():
    with TempDirectory() as tmp:
        src._update_dotfile_with_new_version(root_dir=Path(tmp.path),
                                             version=src.Version(major=4,
                                                                 minor=5,
                                                                 patch=6))
        result = tmp.read(DOTFILE_PATH.as_posix(), encoding='utf8')

        assert result == """\
version: 4.5.6
"""

