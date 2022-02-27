from pathlib import Path

from rivals_workshop_assistant.main import run_main_asyncio
from rivals_workshop_assistant.modes import Mode

root_dir = Path(r"C:\Users\User\AppData\Local\rivalsofaether\workshop\gurren")
exe_dir = Path(
    r"C:\Users\User\AppData\Roaming\AceGM\GMEdit\plugins\rivals-workshop-assistant-gmedit"
)

if __name__ == "__main__":
    # (root_dir / "assistant/.assistant").unlink(missing_ok=True)
    mode = Mode.ALL
    run_main_asyncio(exe_dir, root_dir, mode=mode)
