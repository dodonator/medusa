import logging as log
from pathlib import Path
from typing import Generator
from urllib.parse import urlparse

import pandoc
import requests
from pandoc.types import Link, Pandoc

from medusa.link import PadLink


class Pad:
    name: str
    url: str
    root: str
    filename: Path
    content: str

    def __init__(self, url: str) -> None:
        self.url = url
        self.root = urlparse(url).netloc

    def get(self) -> str:
        if hasattr(self, "content"):
            return self.content

        url = f"{self.url}/download"
        response: requests.models.Response = requests.get(url)
        status_code: int = response.status_code

        if status_code == 200:
            text = response.text
        else:
            log.error(f"Couldn't download pad {self.url}")
            raise Exception("Couldn't download pad {self.url}")
        self.content = text
        return text

    def extract(self) -> list[PadLink]:
        doc: Pandoc = pandoc.read(self.get())
        blocks: list = doc[1]

        # filters all link objects
        link_objects: Generator = (
            block for block in pandoc.iter(blocks) if isinstance(block, Link)
        )

        links: list = []
        link_obj: Link
        for link_obj in link_objects:
            pad_link = PadLink(link_obj)

            if pad_link.root == self.root:
                log.info(f"found link: {pad_link}")
                links.append(pad_link)

        return links
