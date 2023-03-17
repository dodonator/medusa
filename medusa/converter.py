#!/usr/bin/env python3
import logging as log
import re
from pathlib import Path
from typing import Generator

HD_TEMPLATE = "[{}]({}/{})"
OBSIDIAN_TEMPLATE = "[[{}|{}]]"


class Converter:
    root: str
    input_dir: Path
    output_dir: Path

    def __init__(self, root: str, input_dir: Path, output_dir: Path):
        self.root = root
        if input_dir.exists():
            self.input_dir = input_dir

        if not output_dir.exists():
            output_dir.mkdir()
        self.output_dir = output_dir

        self.link_pattern = (
            r"\[(?P<text>.+)\]\((?P<url>"
            + self.root
            + r")/(?P<pad>[A-Za-z0-9\-_\.#\?/%]*)\)"
        )

    def convert_single_pad(self, input_pad: Path) -> int:
        output_pad: Path = self.output_dir / Path(input_pad.name)
        pad_content: str = input_pad.read_text(encoding="UTF-8")

        log.info(f"convert links in {input_pad} into {output_pad}")

        matches = re.findall(self.link_pattern, pad_content)
        for match in matches:
            text, url, pad = match
            clean_pad: str
            if "?" in pad:
                clean_pad = pad.split("?")[0]
            elif "#" in pad:
                clean_pad = pad.split("#")[0]
            else:
                clean_pad = pad
            old: str = HD_TEMPLATE.format(text, url, pad)
            new: str = OBSIDIAN_TEMPLATE.format(clean_pad, text)
            pad_content = pad_content.replace(old, new)

        output_pad.touch()
        output_pad.write_text(pad_content, encoding="UTF-8")
        return len(matches)

    def convert(self):
        all_pads: Generator = self.input_dir.glob("*.md")

        number_of_pads: int = 0
        total_links_number: int = 0
        for pad_path in all_pads:
            number_of_links_converted: int = self.convert_single_pad(pad_path)
            log.info(f"converted {number_of_links_converted} links in {pad_path.name}")
            total_links_number += number_of_links_converted
            number_of_pads += 1

        log.info(f"converted {total_links_number} links in {number_of_pads} pads")
