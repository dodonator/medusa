#!/usr/bin/env python3
import re
from pathlib import Path
from typing import Generator

root = "https://md.chaosdorf.de"
LINK_PATTERN = (
    r"\[(?P<text>.+)\]\((?P<url>.+md\.chaosdorf\.de)/(?P<pad>[A-Za-z0-9\-_\.#\?/%]*)\)"
)
LINK_TEMPLATE = "[{}]({}/{})"


def convert_to_obsidian_links(pad_path: Path) -> int:
    pad_content: str = pad_path.read_text(encoding="UTF-8")
    matches = re.findall(LINK_PATTERN, pad_content)

    for match in matches:
        text, url, pad = match
        clean_pad: str
        if "?" in pad:
            clean_pad = pad.split("?")[0]
        elif "#" in pad:
            clean_pad = pad.split("#")[0]
        else:
            clean_pad = pad
        old: str = LINK_TEMPLATE.format(text, url, pad)
        new: str = f"[[{clean_pad}|{text}]]"
        pad_content = pad_content.replace(old, new)

    pad_path.write_text(pad_content, encoding="UTF-8")
    return len(matches)


pad_directory = Path.cwd() / Path("output")
pad_files: Generator = pad_directory.glob("*.md")

file: Path
for file in pad_files:
    number: int = convert_to_obsidian_links(file)
    print(f"converted {number} links in {file.name}")
