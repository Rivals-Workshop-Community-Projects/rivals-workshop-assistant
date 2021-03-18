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


@pytest.mark.parametrize(
    "update_config, current_version, other_releases, expected_release", [
        pytest.param(src.UpdateConfig.MAJOR,
                     make_version('1.2.3'),
                     [make_release('2.3.4', 'urlb')],
                     make_release('5.0.1', 'urlc')
                     ),
        pytest.param(src.UpdateConfig.MAJOR,
                     make_version('3.0.2'),
                     [make_release('3.0.3', 'urlb')],
                     make_release('3.0.4', 'urlnew'),
                     ),
        pytest.param(src.UpdateConfig.MINOR,
                     make_version('3.0.2'),
                     [make_release('4.0.3', 'urlb'),
                      make_release('4.0.4', 'urlc')],
                     None,
                     ),
        pytest.param(src.UpdateConfig.MINOR,
                     make_version('3.0.2'),
                     [make_release('3.0.3', 'urlb')],
                     make_release('3.0.4', 'urlc')
                     ),
        pytest.param(src.UpdateConfig.PATCH,
                     make_version('3.0.2'),
                     [make_release('4.1.3', 'urlb'),
                      make_release('3.2.3', 'urlc')],
                     make_release('3.0.8', 'urld')),
        pytest.param(src.UpdateConfig.NONE,
                     make_version('3.0.2'),
                     [make_release('3.0.3', 'urlb'),
                      make_release('3.0.4', 'urlc')],
                     None,
                     ),
    ]
)
def test__get_release_to_install_from_config_and_releases(
        update_config, current_version, other_releases, expected_release
):
    releases = ([src.Release(version=current_version, download_url='urla')]
                + other_releases
                )
    if expected_release is not None:
        releases += [expected_release]

    result = src._get_release_to_install_from_config_and_releases(
        update_config=update_config,
        releases=releases,
        current_version=current_version
    )
    assert result == expected_release
