import os
import zipfile
from pathlib import Path
import subprocess
import shutil

exe_name = "rivals_workshop_assistant"

vscode_extension_project_path = Path(
    r"E:\Users\User\WebstormProjects\vscode_extension\rivals-lib"
)
vscode_extension_path = vscode_extension_project_path / r"out"

gmedit_extension_project_path = Path(
    r"D:/Users/User/IdeaProjects/rivals-workshop-assistant-gmedit"
)
gmedit_extension_name = Path("rivals-workshop-assistant-gmedit")
gmedit_extension_path = gmedit_extension_project_path / gmedit_extension_name

exe_path = fr"dist/{exe_name}.exe"

# version_type = 'major'
# version_type = 'minor'
version_type = "patch"


def build_exe():
    build_script = (
        "pyinstaller --noconfirm --onefile --console --name "
        f'"{exe_name}" '
        '"D:/Users/User/PycharmProjects/rivals-workshop-assistant'
        '/rivals_workshop_assistant/main.py"'
    )
    subprocess.run(build_script)


def build_vscode():
    shutil.copy(src=exe_path, dst=vscode_extension_path)

    wd = os.getcwd()
    os.chdir(vscode_extension_project_path)
    vscode_publish_script = f"vsce publish {version_type}"
    subprocess.call(vscode_publish_script, shell=True)
    os.chdir(wd)


def build_gmedit():
    shutil.copy(src=exe_path, dst=gmedit_extension_path)

    wd = os.getcwd()
    os.chdir(vscode_extension_project_path)

    zip_path = gmedit_extension_project_path / "rivals-workshop-assistant-gmedit.zip"
    with zipfile.ZipFile(zip_path, "w") as release_zip:
        for path in gmedit_extension_path.glob("*"):
            release_zip.write(path, arcname=gmedit_extension_name / path.name)

    os.chdir(wd)


if __name__ == "__main__":
    build_exe()
