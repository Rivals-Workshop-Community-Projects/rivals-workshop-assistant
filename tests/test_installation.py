import datetime

import pytest

from rivals_workshop_assistant.dotfile_mod import yaml_load
from rivals_workshop_assistant.injection import installation as src
from tests.testing_helpers import make_version, make_release, TEST_DATE_STRING


def test__make_update_config_empty():
    config_text = ""

    result = src._make_update_config(config_text)
    assert result == src.UpdateConfig.PATCH


@pytest.mark.parametrize(
    "config_value, expected",
    [
        pytest.param("major", src.UpdateConfig.MAJOR),
        pytest.param("minor", src.UpdateConfig.MINOR),
        pytest.param("patch", src.UpdateConfig.PATCH),
        pytest.param("none", src.UpdateConfig.NONE),
    ],
)
def test__make_update_config_major_level(config_value, expected):
    config_text = f"""\
{src.UPDATE_LEVEL_NAME}: {config_value}"""

    result = src._make_update_config(config_text)
    assert result == expected


def test__get_current_release_from_empty_dotfile():
    dotfile = yaml_load("")
    result = src.get_current_version_from_dotfile(dotfile)
    assert result is None


def test__get_current_release_from_dotfile():
    dotfile = yaml_load("version: 3.2.1")
    result = src.get_current_version_from_dotfile(dotfile)
    assert result == make_version("3.2.1")


def test__get_dotfile_with_new_release():
    version = src.Version(major=10, minor=11, patch=12)
    dotfile = yaml_load("version: 3.2.1")

    result = src._get_dotfile_with_new_version_and_last_updated(
        version=version,
        last_updated=datetime.date.fromisoformat(TEST_DATE_STRING),
        dotfile=dotfile,
    )
    assert result == f"version: 10.11.12\nlast_updated: {TEST_DATE_STRING}\n"


def test__get_dotfile_with_new_release_with_other_data():
    release = make_version("10.11.12")
    dotfile = yaml_load(
        """\
something_else: version
version: 3.2.1"""
    )

    result = src._get_dotfile_with_new_version_and_last_updated(
        version=release,
        last_updated=datetime.date.fromisoformat(TEST_DATE_STRING),
        dotfile=dotfile,
    )
    assert (
        result
        == f"""\
something_else: version
version: 10.11.12
last_updated: {TEST_DATE_STRING}
"""
    )


@pytest.mark.parametrize(
    "update_config, current_version, other_releases, expected_release",
    [
        pytest.param(
            src.UpdateConfig.MAJOR,
            make_version("1.2.3"),
            [make_release("2.3.4", "urlb")],
            make_release("5.0.1", "urlc"),
        ),
        pytest.param(
            src.UpdateConfig.MAJOR,
            make_version("3.0.2"),
            [make_release("3.0.3", "urlb")],
            make_release("3.0.4", "urlnew"),
        ),
        pytest.param(
            src.UpdateConfig.MINOR,
            make_version("3.0.2"),
            [make_release("4.0.3", "urlb"), make_release("4.0.4", "urlc")],
            None,
        ),
        pytest.param(
            src.UpdateConfig.MINOR,
            make_version("3.0.2"),
            [make_release("3.0.3", "urlb")],
            make_release("3.0.4", "urlc"),
        ),
        pytest.param(
            src.UpdateConfig.MINOR,
            None,
            [make_release("3.0.3", "urlb"), make_release("3.0.4", "urlc")],
            make_release("3.0.5", "urld"),
        ),
        pytest.param(
            src.UpdateConfig.PATCH,
            make_version("3.0.2"),
            [make_release("4.1.3", "urlb"), make_release("3.2.3", "urlc")],
            make_release("3.0.8", "urld"),
        ),
        pytest.param(
            src.UpdateConfig.NONE,
            make_version("3.0.2"),
            [make_release("3.0.3", "urlb"), make_release("3.0.4", "urlc")],
            None,
        ),
        pytest.param(
            src.UpdateConfig.NONE,
            None,
            [make_release("3.0.3", "urlb"), make_release("3.0.4", "urlc")],
            make_release("3.0.5", "urld"),
        ),
    ],
)
def test__get_release_to_install_from_config_and_releases(
    update_config, current_version, other_releases, expected_release
):
    releases = other_releases

    if current_version is not None:
        releases += [src.Release(version=current_version, download_url="urla")]
    if expected_release is not None:
        releases += [expected_release]

    result = src._get_legal_release_to_install(
        update_config=update_config, releases=releases, current_version=current_version
    )
    assert result == expected_release


@pytest.mark.parametrize(
    "last_updated_string, today_string, expected",
    [
        pytest.param("2019-12-04", "2019-12-05", True),
        pytest.param("2019-12-04", "2019-12-04", False),
    ],
)
def test__get_last_updated_from_dotfile(last_updated_string, today_string, expected):
    dotfile = yaml_load(
        f"""\
other: blah
last_updated: {last_updated_string}"""
    )

    should_update = src._get_should_update_from_dotfile_and_date(
        dotfile=dotfile, today=datetime.date.fromisoformat(today_string)
    )

    assert should_update == expected
