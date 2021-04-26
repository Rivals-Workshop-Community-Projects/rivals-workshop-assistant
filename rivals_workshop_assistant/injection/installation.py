import rivals_workshop_assistant.assistant_config_mod

ANIMS_FOLDER_README = f"""\
Put your aseprite files in here.

If you have `aseprite_path` set in `{rivals_workshop_assistant.assistant_config_mod.PATH}, the assistant will automatically convert them to spritesheets in your sprites folder.
They will be saved as `<anim_name>_strip<num_frames>.png`
This will *overwrite existing sprites with that name.* It is recommended to only change the aseprite file, not the spritesheets, to avoid losing changes.
"""
