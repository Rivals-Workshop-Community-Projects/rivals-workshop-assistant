from rivals_workshop_assistant.injection import installation as src


def test__make_update_config_empty():
    config_text = ""

    result = src._make_update_config(config_text)
    assert result == src.UpdateConfig(allow_major_update=False,
                                      allow_minor_update=False,
                                      allow_patch_update=True)


def test__make_update_config_allow_major():
    config_text = f"""\
{src.ALLOW_MAJOR_UPDATES_NAME}: true"""

    result = src._make_update_config(config_text)
    assert result == src.UpdateConfig(allow_major_update=True,
                                      allow_minor_update=False,
                                      allow_patch_update=True)


def test__make_update_config_disallow_major():
    config_text = f"""\
{src.ALLOW_MAJOR_UPDATES_NAME}: false"""

    result = src._make_update_config(config_text)
    assert result == src.UpdateConfig(allow_major_update=False,
                                      allow_minor_update=False,
                                      allow_patch_update=True)


def test__make_update_config_allow_minor_and_major():
    config_text = f"""\
{src.ALLOW_MAJOR_UPDATES_NAME}: true
{src.ALLOW_MINOR_UPDATES_NAME}: true"""

    result = src._make_update_config(config_text)
    assert result == src.UpdateConfig(allow_major_update=True,
                                      allow_minor_update=True,
                                      allow_patch_update=True)


def test__make_update_config_disallow_patch():
    config_text = f"""\
{src.ALLOW_PATCH_UPDATES_NAME}: false"""

    result = src._make_update_config(config_text)
    assert result == src.UpdateConfig(allow_major_update=False,
                                      allow_minor_update=False,
                                      allow_patch_update=False)
