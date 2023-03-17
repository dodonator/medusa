#!/usr/bin/env python3
import re
from pathlib import Path
from typing import Generator

# TODO: make link syntax conversion modular
# TODO: iterate over all files and substitute the link syntax

root = "https://md.chaosdorf.de"
LINK_PATTERN = (
    r"\[(?P<text>.+)\]\((?P<url>.+md\.chaosdorf\.de)/(?P<pad>[A-Za-z0-9\-_\.#\?/]*)\)"
)
LINK_TEMPLATE = "[{}]({}/{})"

pad_directory = Path.cwd() / Path("output")
pad_files: Generator = pad_directory.glob("*.md")

file: Path
for file in pad_files:
    pad_content: str = file.read_text(encoding="UTF-8")
    m = re.findall(LINK_PATTERN, pad_content)
    for match in m:
        text, url, pad = match
        # TODO: clean pad from queries
        old: str = LINK_TEMPLATE.format(text, url, pad)
        new: str = f"[[{pad}|{text}]]"
        pad_content = pad_content.replace(old, new)

    file.write_text(pad_content, encoding="UTF-8")
