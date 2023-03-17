#!/usr/bin/env python3
import re
from pathlib import Path
from typing import Generator

# TODO: make link syntax conversion modular
# TODO: iterate over all files and substitute the link syntax

LINK_PATTERN = (
    r"\[(?P<text>.+)\]\((?P<url>.+md\.chaosdorf\.de)/(?P<pad>[A-Za-z0-9\-_\.#\?/]*)\)"
)

pad_dir = Path("/home/dodo/dev/Python/obsidian_pipeline/obsidian_pipeline/output")

pads_files: Generator = pad_dir.glob("*.md")

file: Path = Path(
    "/home/dodo/dev/Python/obsidian_pipeline/obsidian_pipeline/navigation.md"
)
content: str = file.read_text(encoding="UTF-8")
m = re.findall(LINK_PATTERN, content)

for match in m:
    text, url, pad = match
    # TODO: clean pad from queries
    print(f"[[{pad}|{text}]]")

# TODO: re substitution
