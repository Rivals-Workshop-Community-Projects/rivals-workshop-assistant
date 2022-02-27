import subprocess

from loguru import logger

from rivals_workshop_assistant.aseprite_handling import (
    AsepritePathParams,
    AsepriteConfigParams,
)
from rivals_workshop_assistant.aseprite_handling.anims import save_anims
from rivals_workshop_assistant.aseprite_handling.aseprites import Aseprite
from rivals_workshop_assistant.assistant_config_mod import (
    get_aseprite_program_path,
    get_hurtboxes_enabled,
    get_is_ssl,
)
from rivals_workshop_assistant.character_config_mod import get_has_small_sprites
from rivals_workshop_assistant.run_context import RunContext
from rivals_workshop_assistant.script_handling.script_mod import Script


async def update_anims(
    run_context: RunContext,
    scripts: list[Script],
    aseprites: list[Aseprite],
):
    aseprite_program_path = get_aseprite_program_path(run_context.assistant_config)
    if aseprite_program_path:
        version = subprocess.check_output(
            [f"{aseprite_program_path}", "--version"]
        ).decode("utf8")

        logger.info(f"Aseprite version is: {version}")
        await save_anims(
            path_params=AsepritePathParams(
                exe_dir=run_context.exe_dir,
                root_dir=run_context.root_dir,
                aseprite_program_path=aseprite_program_path,
            ),
            config_params=AsepriteConfigParams(
                has_small_sprites=get_has_small_sprites(
                    scripts=scripts, character_config=run_context.character_config
                ),
                hurtboxes_enabled=get_hurtboxes_enabled(
                    assistant_config=run_context.assistant_config
                ),
                is_ssl=get_is_ssl(assistant_config=run_context.assistant_config),
            ),
            aseprites=aseprites,
        )
