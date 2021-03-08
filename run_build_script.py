import subprocess
import shutil

exe_name = 'rivals_workshop_assistant'

if __name__ == '__main__':
    script = ('pyinstaller --noconfirm --onefile --console --name '
              f'"{exe_name}" '
              '"D:/Users/User/PycharmProjects/rivals-workshop-assistant'
              '/rivals_workshop_assistant/main.py"')

    subprocess.run(script)

    exe_path = fr"dist/{exe_name}.exe"
    extension_path = (r"E:\Users\User\WebstormProjects\vscode_extension"
                      r"\rivals-lib\out")

    shutil.copy(src=exe_path, dst=extension_path)
