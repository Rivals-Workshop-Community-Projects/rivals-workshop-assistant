from rivals_workshop_assistant.asset_handling import get_required_assets, save_assets
from rivals_workshop_assistant.codegen import handle_codegen
from rivals_workshop_assistant.injection import handle_injection


def main():
    scripts = read_scripts()

    scripts = handle_codegen(scripts)
    scripts = handle_injection(scripts)

    save_scripts(scripts)

    assets = get_required_assets(scripts)
    save_assets(assets)


def read_scripts():
    raise NotImplementedError


def save_scripts(scripts):
    raise NotImplementedError


