#!/usr/bin/env python3
from pathlib import Path
from typing import Generator

import pandoc
import requests
from pandoc.types import Link, Pandoc
from utils import clean_url, pad_id_from_url


class Crawler:
    root: str
    output_dir: Path

    def __init__(self, root_url: str, output_dir: Path | None = None):
        self.root = root_url
        self.found_pads = set()

        if output_dir is None:
            self.output_dir = Path.cwd() / Path("output")
        else:
            self.output_dir = output_dir

        if not self.output_dir.exists():
            self.output_dir.mkdir()

    def get(self, pad_id: str) -> str:
        pad_url: str = f"{self.root}/{pad_id}/download"
        response = requests.get(pad_url)
        if response.status_code == 200:
            return response.text
        else:
            return ""

    def extract(self, pad_content: str) -> list[str]:
        doc: Pandoc = pandoc.read(pad_content)

        blocks = doc[1]
        link_objects: Generator = (
            block for block in pandoc.iter(blocks) if isinstance(block, Link)
        )

        linked_pads: list = []
        for link in link_objects:
            link: Link
            target = link[2]  # Link(Attr, [Inline], Target)
            url: str = clean_url(target[0])
            if url.startswith(self.root):
                pad_id = pad_id_from_url(url)
                linked_pads.append(pad_id)

        return linked_pads

    def crawl(self, start_pad: str):
        to_check: set = set((start_pad,))
        checked: set = set()

        while to_check:
            # get an pad
            current_pad = to_check.pop()

            # download pad
            text = self.get(current_pad)

            # extract links to other pads
            new_pads: set = set(self.extract(text)) - checked

            # add new pads to queue
            to_check.update(new_pads)
            checked.add(current_pad)

        return checked

    def download(self, pad_id):
        text: str = self.get(pad_id)
        filename = f"{pad_id}.md"
        filepath = self.output_dir / Path(filename)

        with filepath.open("w", encoding="UTF-8") as stream:
            stream.write(text)
