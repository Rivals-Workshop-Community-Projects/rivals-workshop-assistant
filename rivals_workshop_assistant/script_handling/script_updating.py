from typing import List

from rivals_workshop_assistant.aseprite_handling import Anim
from rivals_workshop_assistant.aseprite_handling.anims import get_anims
from rivals_workshop_assistant.aseprite_handling.aseprites import Aseprite
from rivals_workshop_assistant.run_context import RunContext
from rivals_workshop_assistant.script_handling.code_generation import handle_codegen
from rivals_workshop_assistant.script_handling.injection import handle_injection
from rivals_workshop_assistant.script_handling.script_mod import Script, save_scripts
from rivals_workshop_assistant.script_handling.warning_handling import handle_warning


def update_scripts(
    run_context: RunContext, scripts: list[Script], aseprites: list[Aseprite]
):
    # I don't like that we need to load all anims to update scripts.
    # Instead, could save the attack timing info to the dotfile when animations run,
    # and then propagate to scripts. That would require doing animations first each run.
    anims = get_anims(aseprites)
    handle_scripts(
        run_context=run_context,
        scripts=scripts,
        anims=anims,
    )
    save_scripts(run_context.root_dir, scripts)


def handle_scripts(
    run_context: RunContext,
    scripts: List[Script],
    anims: List[Anim],
):
    handle_warning(assistant_config=run_context.assistant_config, scripts=scripts)
    handle_codegen(scripts)
    handle_injection(run_context, scripts=scripts, anims=anims)
