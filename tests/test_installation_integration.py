from pathlib import Path

import pytest
from testfixtures import TempDirectory

from rivals_workshop_assistant.injection.library import INJECT_FOLDER
from rivals_workshop_assistant.injection import installation as src
from testing_helpers import make_script, ScriptWithPath

pytestmark = pytest.mark.slow


def test__get_update_config():
    with TempDirectory() as tmp:
        make_script(tmp, ScriptWithPath(
            path=INJECT_FOLDER / Path(src.INJECT_CONFIG_NAME),
            content=f"""\

{src.ALLOW_MINOR_UPDATES_NAME}: true


{src.ALLOW_PATCH_UPDATES_NAME}: true

"""))

        result = src.get_update_config(Path(tmp.path))
        assert result == src.UpdateConfig(allow_major_update=False,
                                          allow_minor_update=True,
                                          allow_patch_update=True)


def test__get_releases():
    result = src.get_releases()

    assert len(result) > 0 and type(result[0]) == src.Release
    # Not going to mock it out, just make sure we get
    #   something

