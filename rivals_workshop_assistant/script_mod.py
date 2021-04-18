from pathlib import Path
from datetime import datetime


class Script:
    def __init__(
        self,
        path: Path,
        modified_time: datetime,
        original_content: str,
        working_content: str = None,
    ):
        self.path = path
        self.modified_time = modified_time
        self.original_content = original_content

        if working_content is None:
            self.working_content = original_content
        else:
            self.working_content = working_content

    def save(self, root_dir: Path):
        with open((root_dir / self.path), "w", newline="\n") as f:
            f.write(self.working_content)

    def __eq__(self, other):
        return (
            self.path == other.path
            and self.original_content == other.original_content
            and self.working_content == other.working_content
        )
