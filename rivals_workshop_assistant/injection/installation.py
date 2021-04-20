import dataclasses
import datetime
import enum
import io
import os
import shutil
import tempfile
import typing
from pathlib import Path
import zipfile

import requests

import rivals_workshop_assistant.paths as paths
from . import paths as inject_paths
from ..info_files import (
    _yaml_load,
    LAST_UPDATED,
    VERSION,
)

UPDATE_LEVEL_NAME = "update_level"


class UpdateConfig(enum.Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    NONE = "none"


UPDATE_LEVEL_DEFAULT = UpdateConfig.PATCH


ASEPRITE_PATH_NAME = "aseprite_path"

DEFAULT_CONFIG = fr"""\
{UPDATE_LEVEL_NAME}: {UPDATE_LEVEL_DEFAULT.value}
    # What kind of library updates to allow. 
    # {UpdateConfig.MAJOR.value} = All updates are allowed, even if they may 
    #   break existing code.
    # {UpdateConfig.MINOR.value} = Don't allow breaking changes to existing 
    #   functions, but do allow new functions. Could cause name collisions.
    # {UpdateConfig.PATCH.value} = Only allow changes to existing functions 
    #   that fix bugs or can't break current functionality.
    # {UpdateConfig.NONE.value} = No updates.
    
# {ASEPRITE_PATH_NAME}: <REPLACE ME, and remove # from beginning of this line>
    # Point this to your Aseprite.exe absolute path, for example: C:\Program Files\Aseprite\aseprite.exe
    # This is needed for the assistant to automatically export your animations to spritesheets.
    # If you use Steam for Aseprite, you can find the path with:
    #   1. The aseprite page of your library
    #   2. The gear icon at the top right
    #   3. Manage
    #   4. Browse Local Files\
    #   5. Copy the path of Aseprite.exe
"""

ANIMS_FOLDER_README = f"""\
Put your aseprite files in here.

If you have `aseprite_path` set in `{paths.ASSISTANT_CONFIG_PATH}, the assistant will automatically convert them to spritesheets in your sprites folder.
They will be saved as `<anim_name>_strip<num_frames>.png`
This will *overwrite existing sprites with that name.* It is recommended to only change the aseprite file, not the spritesheets, to avoid losing changes.
"""


@dataclasses.dataclass
class Version:
    major: int = 0
    minor: int = 0
    patch: int = 0

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __gt__(self, other):
        return (
            self.major > other.major
            or (self.major == other.major and self.minor > other.minor)
            or (
                self.major == other.major
                and self.minor == other.minor
                and self.patch > other.patch
            )
        )


@dataclasses.dataclass
class Release:
    version: Version
    download_url: str

    @classmethod
    def from_github_response(cls, response_dict):
        major, minor, patch = response_dict["tag_name"].split("-")[0].split(".")
        return cls(
            version=Version(major=major, minor=minor, patch=patch),
            download_url=response_dict["zipball_url"],
        )

    def __lt__(self, other: "Release"):
        return self.version < other.version


def update_injection_library(root_dir: Path, dotfile: dict):
    """Controller"""
    if should_update(dotfile):
        current_version = get_current_version_from_dotfile(dotfile)
        release_to_install = get_release_to_install(root_dir, current_version)

        update_dotfile_after_update(
            release_to_install.version if release_to_install else current_version,
            datetime.date.today(),
            dotfile,
        )

        if (
            release_to_install is not None
            and current_version != release_to_install.version
        ):
            install_release(root_dir, release_to_install)


def should_update(dotfile: dict) -> bool:
    today = datetime.date.today()
    return _get_should_update_from_dotfile_and_date(dotfile, today)


def _get_should_update_from_dotfile_and_date(
    dotfile: dict, today: datetime.date
) -> bool:
    default_date = datetime.date.fromisoformat("1996-01-01")

    last_update_day = dotfile.get(LAST_UPDATED, default_date)

    days_passed = (today - last_update_day).days
    return days_passed > 0


def get_release_to_install(root_dir: Path, current_version: Version) -> Release:
    """Controller"""
    update_config = get_update_config(root_dir)
    releases = get_releases()
    release_to_install = _get_legal_release_to_install(
        update_config, releases, current_version
    )
    return release_to_install


def get_update_config(root_dir: Path) -> UpdateConfig:
    """Controller"""
    config_text = _read_config(root_dir)
    update_config = _make_update_config(config_text)
    return update_config


def _read_config(root_dir: Path) -> str:
    """Controller"""
    try:
        config_text = (root_dir / paths.ASSISTANT_CONFIG_PATH).read_text()
        return config_text
    except FileNotFoundError:
        return ""


def _make_update_config(config_text: str) -> UpdateConfig:
    config_yaml: typing.Optional[dict] = _yaml_load(config_text)
    return UpdateConfig(config_yaml.get("update_level", UpdateConfig.PATCH))


def get_releases() -> list[Release]:
    """Controller"""
    release_dicts = requests.get(
        f"https://api.github.com/repos"
        f"/{paths.REPO_OWNER}/{paths.REPO_NAME}/releases"
    ).json()
    releases = [
        Release.from_github_response(release_dict)
        for release_dict in release_dicts
        if not release_dict["prerelease"]
    ]
    return releases


def _get_legal_release_to_install(
    update_config: UpdateConfig,
    releases: list[Release],
    current_version: typing.Optional[Version],
) -> typing.Optional[Release]:
    if current_version is None:
        candidates = releases.copy()
    else:
        candidates = _get_legal_releases(
            update_config=update_config,
            releases=releases,
            current_version=current_version,
        )
    if candidates:
        newest_version = max(candidates)
        return newest_version
    else:
        return None


def _get_legal_releases(
    update_config: UpdateConfig, releases: list[Release], current_version: Version
) -> list[Release]:
    """Releases are constrained based on config and current version."""
    if update_config == UpdateConfig.NONE:
        return []

    candidates = releases.copy()

    if update_config == UpdateConfig.MINOR:
        candidates = [
            candidate
            for candidate in candidates
            if candidate.version.major == current_version.major
            and candidate.version > current_version
        ]

    elif update_config == UpdateConfig.PATCH:
        candidates = [
            candidate
            for candidate in candidates
            if candidate.version.major == current_version.major
            and candidate.version.minor == current_version.minor
            and candidate.version > current_version
        ]
    return candidates


def get_current_version_from_dotfile(dotfile: dict) -> typing.Optional[Version]:
    version_string: str = dotfile.get("version", None)
    if version_string is None:
        return None

    major, minor, patch = (int(val) for val in version_string.split("."))
    return Version(major=major, minor=minor, patch=patch)


def install_release(root_dir: Path, release: Release):
    """Controller"""
    _delete_old_release(root_dir)
    _download_and_unzip_release(root_dir, release)


def _delete_old_release(root_dir: Path):
    """Controller"""
    inject_path = root_dir / inject_paths.INJECT_FOLDER
    try:
        shutil.rmtree(inject_path)
    except FileNotFoundError:
        pass  # Nothing to delete


def _download_and_unzip_release(root_dir: Path, release: Release):
    """Controller"""
    with tempfile.TemporaryDirectory() as tmp:
        response = requests.get(release.download_url)
        zipped_release = zipfile.ZipFile(io.BytesIO(response.content))
        zipped_release.extractall(path=tmp)

        release_root = list(Path(tmp).glob("*"))[0]  # gets the subfolder

        os.rename(release_root / "inject", release_root / ".inject")
        shutil.move(
            src=release_root / ".inject", dst=root_dir / inject_paths.INJECT_FOLDER
        )


def update_dotfile_after_update(
    version: Version, last_updated: datetime.date, dotfile: dict
) -> dict:
    dotfile[VERSION] = str(version)
    dotfile[LAST_UPDATED] = last_updated
    return dotfile
