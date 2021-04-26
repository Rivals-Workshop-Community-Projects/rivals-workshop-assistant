import dataclasses
import datetime
import io
import os
import shutil
import tempfile
import typing
import zipfile
from pathlib import Path

import requests

import rivals_workshop_assistant.paths
from rivals_workshop_assistant import paths as paths
from rivals_workshop_assistant.assistant_config_mod import UpdateConfig
from rivals_workshop_assistant.dotfile_mod import (
    LAST_UPDATED_FIELD,
    get_library_version_string,
    get_assistant_version_string,
    ASSISTANT_VERSION_FIELD,
    LIBRARY_VERSION_FIELD,
)


# TODO NOW merge common functions into a class


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
    release_dict: dict

    @classmethod
    def from_github_response(cls, response_dict):
        major, minor, patch = response_dict["tag_name"].split("-")[0].split(".")
        return cls(
            version=Version(major=major, minor=minor, patch=patch),
            download_url=response_dict["zipball_url"],
            release_dict=response_dict,
        )

    def __lt__(self, other: "Release"):
        return self.version < other.version

    def get_asset_url(self, asset_name: str) -> typing.Optional[str]:
        assets = self.release_dict["assets"]
        assets_with_name = [asset for asset in assets if asset["name"] == asset_name]
        if len(assets_with_name) >= 1:
            if len(assets_with_name) > 1:
                print(
                    f"WARN: Multiple assets with name {asset_name} for release {self.release_dict['url']}"
                )
            return assets_with_name[0]["browser_download_url"]
        else:
            return None


def update(root_dir: Path, dotfile: dict, config: dict):
    """Runs all self-updates.
    Controller"""
    if should_update(dotfile):
        current_assistant_version = get_current_assistant_version(dotfile)
        new_assistant_version = update_assistant(root_dir, current_assistant_version)

        current_library_version = get_current_library_version(dotfile)
        new_library_version = update_library(
            root_dir, current_library_version, config=config
        )

        update_dotfile_after_update(
            assistant_version=new_assistant_version,
            library_version=new_library_version,
            last_updated=datetime.date.today(),
            dotfile=dotfile,
        )


def update_assistant(
    root_dir: Path, current_version: Version
) -> typing.Optional[Version]:
    """Controller"""
    current_exe_path = paths.get_exe_path()
    if current_exe_path.name != paths.ASSISTANT_EXE_NAME:
        print(
            f"WARN: assistant exe at {current_exe_path} should be named {paths.ASSISTANT_EXE_NAME}.\n"
            f"\tExe will not update."
        )
        return

    release_to_install = get_assistant_release_to_install(
        current_version=current_version
    )

    if release_to_install is not None and current_version != release_to_install.version:
        install_assistant_release(root_dir, release_to_install)

    return release_to_install.version if release_to_install else current_version


def update_library(root_dir: Path, current_version: Version, config: dict):
    """Controller"""
    release_to_install = get_library_release_to_install(
        current_version=current_version, config=config
    )

    if release_to_install is not None and current_version != release_to_install.version:
        install_library_release(root_dir, release_to_install)

    return release_to_install.version if release_to_install else current_version


def should_update(dotfile: dict) -> bool:
    today = datetime.date.today()
    return _get_should_update_from_dotfile_and_date(dotfile, today)


def _get_should_update_from_dotfile_and_date(
    dotfile: dict, today: datetime.date
) -> bool:
    default_date = datetime.date.fromisoformat("1996-01-01")

    last_update_day = dotfile.get(LAST_UPDATED_FIELD, default_date)

    days_passed = (today - last_update_day).days
    return days_passed > 0


def get_assistant_release_to_install(current_version: Version) -> Release:
    """Controller"""
    assistant_releases = get_assistant_releases()
    return assistant_releases[-1]


def get_library_release_to_install(current_version: Version, config: dict) -> Release:
    """Controller"""
    update_config = _make_update_config(config)
    library_releases = get_library_releases()
    release_to_install = _get_legal_library_release_to_install(
        update_config, library_releases, current_version
    )
    return release_to_install


def _make_update_config(config: dict) -> UpdateConfig:
    return UpdateConfig(config.get("update_level", UpdateConfig.PATCH))


def get_assistant_releases() -> list[Release]:
    """Controller"""
    release_dicts = requests.get(
        f"https://api.github.com/repos"
        f"/{paths.REPO_OWNER}/{paths.ASSISTANT_REPO_NAME}/releases"
    ).json()
    releases = [
        Release.from_github_response(release_dict)
        for release_dict in release_dicts
        if not release_dict["prerelease"]
    ]
    return releases


def get_library_releases() -> list[Release]:
    """Controller"""
    release_dicts = requests.get(
        f"https://api.github.com/repos"
        f"/{paths.REPO_OWNER}/{paths.LIBRARY_REPO_NAME}/releases"
    ).json()
    releases = [
        Release.from_github_response(release_dict)
        for release_dict in release_dicts
        if not release_dict["prerelease"]
    ]
    return releases


def _get_legal_library_release_to_install(
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


def get_current_library_version(dotfile: dict) -> typing.Optional[Version]:
    version_string = get_library_version_string(dotfile)
    if version_string is None:
        return None
    return get_version_from_version_string(version_string)


def get_current_assistant_version(dotfile: dict) -> typing.Optional[Version]:
    version_string = get_assistant_version_string(dotfile)
    if version_string is None:
        return None
    return get_version_from_version_string(version_string)


def get_version_from_version_string(version_string: str):
    major, minor, patch = (int(val) for val in version_string.split("."))
    return Version(major=major, minor=minor, patch=patch)


def install_assistant_release(root_dir: Path, release: Release):
    """Controller"""
    print(f"Updating assistant to version: {release.version}")

    with tempfile.TemporaryDirectory() as tmp:
        request = release.get_asset_url(paths.ASSISTANT_EXE_NAME)
        response = requests.get(request)
        tmp_exe_path = Path(tmp) / paths.ASSISTANT_TMP_EXE_NAME
        with open(tmp_exe_path, mode="wb") as exe_file:
            exe_file.write(response.content)

        if not os.access(tmp_exe_path, os.X_OK):
            print("WARN: Downloaded assistant exe looks malformed. Not updating.")
            return

        # Rename current exe to .bak
        current_exe_path = paths.get_exe_path()
        current_exe_path_as_bak = current_exe_path.with_name(
            current_exe_path.stem + ".bak"
        )
        os.rename(src=current_exe_path, dst=current_exe_path_as_bak)

        # Move new exe in as .exe
        shutil.move(src=tmp_exe_path, dst=current_exe_path)


def install_library_release(root_dir: Path, release: Release):
    """Controller"""
    _delete_old_library_release(root_dir)
    _download_and_unzip_library_release(root_dir, release)


def _delete_old_library_release(root_dir: Path):
    """Controller"""
    inject_path = root_dir / rivals_workshop_assistant.paths.INJECT_FOLDER
    try:
        shutil.rmtree(inject_path)
    except FileNotFoundError:
        pass  # Nothing to delete


def _download_and_unzip_library_release(root_dir: Path, release: Release):
    """Controller"""
    with tempfile.TemporaryDirectory() as tmp:
        response = requests.get(release.download_url)
        zipped_release = zipfile.ZipFile(io.BytesIO(response.content))
        zipped_release.extractall(path=tmp)

        release_root = list(Path(tmp).glob("*"))[0]  # gets the subfolder

        os.rename(release_root / "inject", release_root / ".inject")
        shutil.move(
            src=release_root / ".inject",
            dst=root_dir / rivals_workshop_assistant.paths.INJECT_FOLDER,
        )


def update_dotfile_after_update(
    assistant_version: Version,
    library_version: Version,
    last_updated: datetime.date,
    dotfile: dict,
) -> dict:
    dotfile[ASSISTANT_VERSION_FIELD] = str(assistant_version)
    dotfile[LIBRARY_VERSION_FIELD] = str(library_version)
    dotfile[LAST_UPDATED_FIELD] = last_updated
    return dotfile
