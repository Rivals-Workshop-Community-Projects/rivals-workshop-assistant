from pathlib import Path


def create_file(path: Path, content: str, overwrite=False):
    """Creates or overwrites the file with the given content"""
    path.parent.mkdir(exist_ok=True)
    if not overwrite and path.exists():
        return

    with open(path, "w+", newline="\n") as f:
        f.write(content)
