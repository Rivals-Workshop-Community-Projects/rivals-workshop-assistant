from pathlib import Path

from rivals_workshop_assistant.main import Mode, main

root_dir = Path(r"C:\Users\User\AppData\Local\rivalsofaether\workshop\gurren")
exe_dir = Path(
    r"D:\Users\User\PycharmProjects\rivals-workshop-assistant\rivals_workshop_assistant"
)

if __name__ == "__main__":
    (root_dir / "assistant/.assistant").unlink(missing_ok=True)
    mode = Mode.ALL
    main(exe_dir, root_dir, mode=mode)
