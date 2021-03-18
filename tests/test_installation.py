import pytest

from rivals_workshop_assistant.injection import installation as src


def make_version(version_str: str) -> src.Version:
    major, minor, patch = (int(char) for char in version_str.split('.'))
    return src.Version(major=major, minor=minor, patch=patch)


def make_release(version_str: str, url: str) -> src.Release:
    version = make_version(version_str)
    return src.Release(version=version, download_url=url)


def test__make_update_config_empty():
    config_text = ""

    result = src._make_update_config(config_text)
    assert result == src.UpdateConfig.PATCH


@pytest.mark.parametrize(
    "config_value, expected", [
        pytest.param("major", src.UpdateConfig.MAJOR),
        pytest.param("minor", src.UpdateConfig.MINOR),
        pytest.param("patch", src.UpdateConfig.PATCH),
        pytest.param("none", src.UpdateConfig.NONE)
    ]
)
def test__make_update_config_major_level(config_value, expected):
    config_text = f"""\
{src.UPDATE_LEVEL_NAME}: {config_value}"""

    result = src._make_update_config(config_text)
    assert result == expected


def test__get_current_release_from_empty_dotfile():
    dotfile = ""
    result = src.get_current_release_from_dotfile(dotfile)
    assert result is None


def test__get_current_release_from_dotfile():
    dotfile = "version: 3.2.1"
    result = src.get_current_release_from_dotfile(dotfile)
    assert result == make_version('3.2.1')


def test__get_dotfile_with_new_release():
    version = src.Version(major=10, minor=11, patch=12)
    old_dotfile = "version: 3.2.1"

    result = src._get_dotfile_with_new_version(version=version,
                                               old_dotfile=old_dotfile)
    assert result == "version: 10.11.12\n"


def test__get_dotfile_with_new_release_with_other_data():
    release = make_version('10.11.12')
    old_dotfile = """\
something_else: version
version: 3.2.1"""

    result = src._get_dotfile_with_new_version(version=release,
                                               old_dotfile=old_dotfile)
    assert result == """\
something_else: version
version: 10.11.12
"""



