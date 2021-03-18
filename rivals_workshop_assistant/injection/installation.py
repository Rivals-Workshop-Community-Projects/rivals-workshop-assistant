import dataclasses
import enum
import typing
from pathlib import Path

from ruamel.yaml import YAML, StringIO
from github3api import GitHubAPI

from rivals_workshop_assistant.injection import library

yaml_handler = YAML()
github = GitHubAPI()

UPDATE_LEVEL_NAME = 'update_level'

INJECT_CONFIG_NAME = 'inject_config.ini'


class UpdateConfig(enum.Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    NONE = "none"


@dataclasses.dataclass
class Version:
    major: int = 0
    minor: int = 0
    patch: int = 0

    def __str__(self):
        return f'{self.major}.{self.minor}.{self.patch}'

    def __gt__(self, other):
        return (self.major > other.major
                or (self.major == other.major and self.minor > other.minor)
                or (self.major == other.major and self.minor == other.minor
                    and self.patch > other.patch)
                )


@dataclasses.dataclass
class Release:
    version: Version
    download_url: str

    @classmethod
    def from_github_response(cls, response_dict):
        major, minor, patch = (response_dict['tag_name']
                               .split('-')[0]
                               .split('.'))
        return cls(version=Version(major=major, minor=minor, patch=patch),
                   download_url=response_dict['zipball_url'])

    def __gt__(self, other):
        return self.version > other.version


def update_injection_library(root_dir: Path):
    """Controller"""
    current_version = _get_current_version(root_dir)
    release_to_install = get_release_to_install(root_dir, current_version)
    if (release_to_install is not None
            and current_version != release_to_install.version):
        install_release(root_dir, release_to_install)


def get_release_to_install(root_dir: Path, current_version: Version) -> Release:
    """Controller"""
    update_config = get_update_config(root_dir)
    releases = get_releases()
    release_to_install = _get_legal_release_to_install(
        update_config, releases, current_version)
    return release_to_install


def get_update_config(root_dir: Path) -> UpdateConfig:
    """Controller"""
    config_text = _read_config(root_dir)
    update_config = _make_update_config(config_text)
    return update_config


def _read_config(root_dir: Path) -> str:
    """Controller"""
    config_path = root_dir / library.INJECT_FOLDER / INJECT_CONFIG_NAME
    try:
        config_text = config_path.read_text()
        return config_text
    except FileNotFoundError:
        return ''


def _make_update_config(config_text: str) -> UpdateConfig:
    config_yaml: typing.Optional[dict] = yaml_handler.load(config_text)
    if not config_yaml:
        return UpdateConfig.PATCH
    return UpdateConfig(config_yaml.get('update_level', UpdateConfig.PATCH))


def get_current_version(root_dir: Path) -> typing.Optional[Version]:
    """Controller"""
    dotfile_text = read_dotfile(root_dir)


def get_releases() -> list[Release]:
    """Controller"""

    release_dicts = github.get(
        f"/repos/{library.REPO_OWNER}/{library.REPO_NAME}/releases")
    releases = [Release.from_github_response(release_dict)
                for release_dict in release_dicts
                if not release_dict['prerelease']]
    return releases


def _get_legal_release_to_install(
        update_config: UpdateConfig,
        releases: list[Release],
        current_version: typing.Optional[Version]) -> typing.Optional[Release]:
    if current_version is None:
        candidates = releases.copy()
    else:
        candidates = _get_legal_releases(update_config=update_config,
                                         releases=releases,
                                         current_version=current_version)
    if candidates:
        newest_version = max(candidates)
        return newest_version
    else:
        return None


def _get_legal_releases(
        update_config: UpdateConfig,
        releases: list[Release],
        current_version: Version
) -> list[Release]:
    """Releases are constrained based on config and current version."""
    if update_config == UpdateConfig.NONE:
        return []

    candidates = releases.copy()

    if update_config == UpdateConfig.MINOR:
        candidates = [candidate for candidate in candidates
                      if candidate.version.major == current_version.major
                      and candidate.version > current_version]

    elif update_config == UpdateConfig.PATCH:
        candidates = [candidate for candidate in candidates
                      if candidate.version.major == current_version.major
                      and candidate.version.minor == current_version.minor
                      and candidate.version > current_version]
    return candidates


def _get_current_version(root_dir: Path) -> Version:
    """Controller"""
    dotfile = read_dotfile(root_dir)
    return get_current_version_from_dotfile(dotfile)


def get_current_version_from_dotfile(dotfile: str) -> typing.Optional[Version]:
    dotfile_yaml = yaml_handler.load(dotfile)
    if dotfile_yaml is None:
        return None

    version_string: str = dotfile_yaml.get('version', None)
    if version_string is None:
        return None

    major, minor, patch = (int(val) for val in version_string.split('.'))
    return Version(major=major, minor=minor, patch=patch)


def install_release(root_dir: Path, release: Release):
    """Controller"""
    _delete_old_release(root_dir)
    _download_and_unzip_release(root_dir)
    _update_dotfile_with_new_version(root_dir, release.version)


def _delete_old_release(root_dir: Path):
    """Controller"""
    raise NotImplementedError


def _download_and_unzip_release(root_dir: Path):
    """Controller"""
    raise NotImplementedError


def _update_dotfile_with_new_version(root_dir: Path, version: Version):
    """Controller"""
    old_dotfile = read_dotfile(root_dir)
    new_dotfile = _get_dotfile_with_new_version(version, old_dotfile)
    save_dotfile(root_dir, new_dotfile)


def read_dotfile(root_dir: Path):
    """Controller"""
    dotfile_path = root_dir / library.DOTFILE_PATH
    try:
        return dotfile_path.read_text()
    except FileNotFoundError:
        return ''


def _get_dotfile_with_new_version(
        version: Version, old_dotfile: str) -> str:
    dotfile_yaml = yaml_handler.load(old_dotfile)

    if dotfile_yaml is None:
        dotfile_yaml = {}

    dotfile_yaml['version'] = str(version)
    return _yaml_dumps(dotfile_yaml)


def save_dotfile(root_dir: Path, dotfile: str):
    """Controller"""
    dotfile_path = root_dir / library.DOTFILE_PATH
    dotfile_path.parent.mkdir(exist_ok=True)
    with open(dotfile_path, 'w+', newline='\n') as f:
        f.write(dotfile)


def _yaml_dumps(obj) -> str:
    with StringIO() as string_stream:
        yaml_handler.dump(obj, string_stream)
        output_str = string_stream.getvalue()
    return output_str
