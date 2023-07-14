from pathlib import Path
from typing import TextIO
from rich import print

working_dir: Path = Path("/home/dodo/chaosdorf_vault")

translation_table: dict[Path, str] = {}

file: Path
for file in working_dir.iterdir():
    print(file)

    stream: TextIO
    with file.open("r") as stream:
        for line in stream:
            if "/" in line:
                line = line.replace("/", "_")

            if line.startswith("# "):
                title: str = line[2:].strip()

                translation_table[file] = f"{title}.md"
                continue

for file, title in translation_table.items():
    content: str = file.read_text()

    for f, t in translation_table.items():
        content = content.replace(f.name, t)

    file.write_text(content)
    file.rename(working_dir / Path(f"{title}.md"))
