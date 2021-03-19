from pathlib import Path

import pytest
from testfixtures import TempDirectory

from rivals_workshop_assistant.injection.library import INJECT_FOLDER, \
    DOTFILE_PATH
from rivals_workshop_assistant.injection import installation as src
from tests.testing_helpers import make_script, \
    ScriptWithPath, \
    make_release, \
    make_version

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


TEST_RELEASE = make_release(
    '0.0.0',
    'https://github.com/Rivals-Workshop-Community-Projects'
    '/injector-library/archive/0.0.0.zip')


def test__delete_old_release():
    with TempDirectory() as tmp:
        make_script(tmp,
                    ScriptWithPath(
                        path=INJECT_FOLDER / 'test.gml',
                        content='test content'),
                    )

        src._delete_old_release(Path(tmp.path))

        tmp.compare(path=INJECT_FOLDER.as_posix(), expected=())


def test__delete_old_release__none_exists():
    with TempDirectory() as tmp:
        src._delete_old_release(Path(tmp.path))

        tmp.compare(path=INJECT_FOLDER.as_posix(), expected=())


def assert_test_release_installed(tmp):
    file_contents = tmp.read((INJECT_FOLDER / 'logging.gml').as_posix(),
                             encoding='utf8')
    assert file_contents == """\
#define prints()
    // Prints each parameter to console, separated by spaces.
    var _out_string = argument[0]
    for var i = 1; i < argument_count; i++ {
        _out_string += " "
        _out_string += string(argument[i])
    }
    print(_out_string)"""


def test__download_and_unzip_release():
    with TempDirectory() as tmp:
        src._download_and_unzip_release(
            root_dir=Path(tmp.path), release=TEST_RELEASE)
        assert_test_release_installed(tmp)


def test__download_and_unzip_release__directory_already_present():
    with TempDirectory() as tmp:
        tmp.makedir('inject')
        src._download_and_unzip_release(
            root_dir=Path(tmp.path), release=TEST_RELEASE)
        assert_test_release_installed(tmp)


def test__update_dotfile__no_dotfile():
    with TempDirectory() as tmp:
        src._update_dotfile_with_new_version(
            root_dir=Path(tmp.path), version=make_version('4.5.6'))

        dotpath_content = tmp.read(filepath=DOTFILE_PATH.as_posix(),
                                   encoding='utf8')
        assert dotpath_content == 'version: 4.5.6\n'


def test__update_dotfile():
    with TempDirectory() as tmp:
        make_script(tmp, ScriptWithPath(
            path=DOTFILE_PATH, content='version: 3.4.5\n'))
        src._update_dotfile_with_new_version(
            root_dir=Path(tmp.path), version=make_version('4.5.6'))

        dotfile = tmp.read(filepath=DOTFILE_PATH.as_posix(),
                           encoding='utf8')
        assert dotfile == 'version: 4.5.6\n'


def test__install_release():
    with TempDirectory() as tmp:
        make_script(tmp,
                    ScriptWithPath(
                        path=INJECT_FOLDER / 'test.gml',
                        content='test content'),
                    )

        src.install_release(root_dir=Path(tmp.path),
                            release=TEST_RELEASE)

        assert_test_release_installed(tmp)
        dotfile = tmp.read(filepath=DOTFILE_PATH.as_posix(),
                           encoding='utf8')
        assert dotfile == 'version: 0.0.0\n'

# def test__update_injection_library__on_empty():
#     with TempDirectory() as tmp:
#         src.update_injection_library(root_dir=Path(tmp.path))
#
#         assert False
