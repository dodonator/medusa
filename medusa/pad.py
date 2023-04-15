import logging as log
from pathlib import Path
import re
from typing import Generator
from urllib.parse import ParseResult, urlparse

import pandoc
import requests
from pandoc.types import Header, Link, Pandoc

from medusa.link import PadLink


class Pad:
    name: str
    title: str
    url: str
    root: str
    filename: Path
    content: str

    def __init__(self, url: str) -> None:
        self.url = url
        parse_result: ParseResult = urlparse(url)
        self.root = parse_result.netloc
        self.name = parse_result.path

    def get_content(self) -> str:
        if hasattr(self, "content"):
            return self.content

        url = f"{self.url}/download"
        response: requests.models.Response = requests.get(url)
        status_code: int = response.status_code

        if status_code == 200:
            content = response.text
        else:
            log.error(f"Couldn't download pad {self.url}")
            raise Exception("Couldn't download pad {self.url}")
        self.content = content
        return content

    def get_title(self) -> str:
        if hasattr(self, "title"):
            return self.title

        doc: Pandoc = pandoc.read(self.get_content())
        meta: list = doc[0]
        blocks: list = doc[1]
        title: str

        header: list[Header] = [
            block for block in blocks if isinstance(block, Header) and block[0] == 1
        ]

        # tries to get title from meta data
        meta_dict: dict = meta[0]
        if "title" in meta_dict:
            title = pandoc.write(meta_dict.get("title")).strip()
            log.info(f"found title {title!r} in meta data")
            return title

        # uses first h1 header as title
        elif header:
            title = pandoc.write(header[0]).strip()
            log.info(f"first header was {title!r}")

        else:
            log.info("no title found")
            title = self.name

        # clean title
        source_pattern = r"[\-~#/ ]+"
        target_pattern = r"_"
        clean_title: str = re.sub(source_pattern, target_pattern, title)
        clean_title = clean_title.strip("_")

        self.title = clean_title

        return clean_title

    def extract(self) -> list[PadLink]:
        doc: Pandoc = pandoc.read(self.get_content())
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

    def __repr__(self) -> str:
        return f"Pad({self.url})"
