import datetime
import typing
from pathlib import Path

import pytest

import rivals_workshop_assistant.assistant_config_mod
from rivals_workshop_assistant import dotfile_mod, assistant_config_mod
import rivals_workshop_assistant.updating as src
from rivals_workshop_assistant.info_files import _yaml_load
from tests.testing_helpers import (
    make_version,
    make_release,
    TEST_DATE_STRING,
    make_run_context,
)
from loguru import logger

logger.remove()


def make_library_updater(
    root_dir=Path("a"), exe_dir=Path("exe_dir"), dotfile=None, config=None
):
    return _make_updater(
        exe_dir=exe_dir,
        root_dir=root_dir,
        dotfile=dotfile,
        assistant_config=config,
        type_=src.LibraryUpdater,
    )


def make_assistant_updater(
    root_dir=Path("a"), exe_dir=Path("exe_dir"), dotfile=None, config=None
):
    return _make_updater(
        exe_dir=exe_dir,
        root_dir=root_dir,
        dotfile=dotfile,
        assistant_config=config,
        type_=src.AssistantUpdater,
    )


def _make_updater(
    exe_dir: Path,
    root_dir: Path,
    dotfile: dict,
    assistant_config: dict,
    type_: typing.Type,
):
    run_context = make_run_context(
        exe_dir=exe_dir,
        root_dir=root_dir,
        dotfile=dotfile,
        assistant_config=assistant_config,
    )
    return type_(run_context)


@pytest.mark.parametrize(
    "config_value, expected",
    [
        pytest.param(
            "major", rivals_workshop_assistant.assistant_config_mod.UpdateLevel.MAJOR
        ),
        pytest.param(
            "minor", rivals_workshop_assistant.assistant_config_mod.UpdateLevel.MINOR
        ),
        pytest.param(
            "patch", rivals_workshop_assistant.assistant_config_mod.UpdateLevel.PATCH
        ),
        pytest.param(
            "none", rivals_workshop_assistant.assistant_config_mod.UpdateLevel.NONE
        ),
    ],
)
def test__make_update_config_major_level(config_value, expected):
    config = {
        rivals_workshop_assistant.assistant_config_mod.LIBRARY_UPDATE_LEVEL_FIELD: config_value
    }

    result = assistant_config_mod.get_library_update_level(config)
    assert result == expected


@pytest.mark.parametrize(
    "make_updater",
    [pytest.param(make_library_updater), pytest.param(make_assistant_updater)],
)
def test__get_current_release_from_empty_dotfile(make_updater: typing.Callable):
    dotfile = _yaml_load("")

    updater = make_updater(dotfile=dotfile)

    assert updater.current_version is None


@pytest.mark.parametrize(
    "make_updater, version",
    [
        pytest.param(make_library_updater, dotfile_mod.LIBRARY_VERSION_FIELD),
        pytest.param(make_assistant_updater, dotfile_mod.ASSISTANT_VERSION_FIELD),
    ],
)
def test__get_current_release_from_dotfile(make_updater: typing.Callable, version):
    dotfile = _yaml_load(f"{version}: 3.2.1")

    updater = make_updater(dotfile=dotfile)

    assert updater.current_version == make_version("3.2.1")


def test__get_dotfile_with_new_release():
    assistant_version = src.Version(major=10, minor=11, patch=12)
    library_version = src.Version(major=13, minor=14, patch=15)
    dotfile = _yaml_load(
        f"{dotfile_mod.LIBRARY_VERSION_FIELD}: 3.2.1\n"
        f"{dotfile_mod.ASSISTANT_VERSION_FIELD}: 4.5.6"
    )

    result = src.update_dotfile_after_update(
        assistant_version=assistant_version,
        library_version=library_version,
        last_updated=datetime.date.fromisoformat(TEST_DATE_STRING),
        dotfile=dotfile,
    )
    assert result == _yaml_load(
        f"{dotfile_mod.ASSISTANT_VERSION_FIELD}: 10.11.12\n"
        f"{dotfile_mod.LIBRARY_VERSION_FIELD}: 13.14.15\n"
        f"last_updated: {TEST_DATE_STRING}\n"
    )


def test__get_dotfile_with_new_release_with_other_data():
    library_version = make_version("13.14.15")
    assistant_version = make_version("10.11.12")
    dotfile = _yaml_load(
        f"""\
something_else: version
{dotfile_mod.LIBRARY_VERSION_FIELD}: 3.2.1\n
{dotfile_mod.ASSISTANT_VERSION_FIELD}: 4.5.6"""
    )

    result = src.update_dotfile_after_update(
        assistant_version=assistant_version,
        library_version=library_version,
        last_updated=datetime.date.fromisoformat(TEST_DATE_STRING),
        dotfile=dotfile,
    )
    assert result == _yaml_load(
        f"""\
something_else: version
{dotfile_mod.LIBRARY_VERSION_FIELD}: 13.14.15
{dotfile_mod.ASSISTANT_VERSION_FIELD}: 10.11.12
last_updated: {TEST_DATE_STRING}
"""
    )


@pytest.mark.parametrize(
    "update_config, current_version, other_releases, expected_release",
    [
        pytest.param(
            rivals_workshop_assistant.assistant_config_mod.UpdateLevel.MAJOR,
            make_version("1.2.3"),
            [make_release("2.3.4", "urlb")],
            make_release("5.0.1", "urlc"),
        ),
        pytest.param(
            rivals_workshop_assistant.assistant_config_mod.UpdateLevel.MAJOR,
            make_version("3.0.2"),
            [make_release("3.0.3", "urlb")],
            make_release("3.0.4", "urlnew"),
        ),
        pytest.param(
            rivals_workshop_assistant.assistant_config_mod.UpdateLevel.MINOR,
            make_version("3.0.2"),
            [make_release("4.0.3", "urlb"), make_release("4.0.4", "urlc")],
            None,
        ),
        pytest.param(
            rivals_workshop_assistant.assistant_config_mod.UpdateLevel.MINOR,
            make_version("3.0.2"),
            [make_release("3.0.3", "urlb")],
            make_release("3.0.4", "urlc"),
        ),
        pytest.param(
            rivals_workshop_assistant.assistant_config_mod.UpdateLevel.MINOR,
            None,
            [make_release("3.0.3", "urlb"), make_release("3.0.4", "urlc")],
            make_release("3.0.5", "urld"),
        ),
        pytest.param(
            rivals_workshop_assistant.assistant_config_mod.UpdateLevel.PATCH,
            make_version("3.0.2"),
            [make_release("4.1.3", "urlb"), make_release("3.2.3", "urlc")],
            make_release("3.0.8", "urld"),
        ),
        pytest.param(
            rivals_workshop_assistant.assistant_config_mod.UpdateLevel.NONE,
            make_version("3.0.2"),
            [make_release("3.0.3", "urlb"), make_release("3.0.4", "urlc")],
            None,
        ),
        pytest.param(
            rivals_workshop_assistant.assistant_config_mod.UpdateLevel.NONE,
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
        releases += [
            src.Release(version=current_version, download_url="urla", release_dict={})
        ]
    if expected_release is not None:
        releases += [expected_release]

    result = src._get_legal_library_release_to_install(
        update_level=update_config, releases=releases, current_version=current_version
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
    dotfile = _yaml_load(
        f"""\
other: blah
last_updated: {last_updated_string}"""
    )

    should_update = src._get_should_update_from_dotfile_and_date(
        dotfile=dotfile, today=datetime.date.fromisoformat(today_string)
    )

    assert should_update == expected
