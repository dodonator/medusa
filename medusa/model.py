from __future__ import annotations
import logging as log
from pathlib import Path
import re
from typing import Generator
from urllib.parse import ParseResult, urljoin, urlparse

import pandoc
import requests
from pandoc.types import Header, Link, Pandoc


class PadLink:
    raw: str
    clean: str
    root: str
    text: str
    _pad: Pad

    def __init__(self, link_obj: Link):
        # Link(Attr, [Inline], Target)
        _, inline, target = link_obj

        self.raw = pandoc.write(link_obj).strip()
        url: ParseResult = urlparse(target[0])

        # remove queries and fragments
        clean_url = urljoin(url.geturl(), url.path)
        self.clean = clean_url

        self.root = url.netloc
        self.pad_id = url.path[1:]
        self.text = pandoc.write(inline).strip()

    @property
    def pad(self):
        if hasattr(self, "_pad"):
            return self._pad
        self._pad = Pad(self.clean)
        return self._pad

    def __repr__(self) -> str:
        return f"PadLink(text='{self.text}',url='{self.clean}')"


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

    def get_content(self) -> str:  # TODO: replace with property
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

    def get_title(self) -> str:  # TODO: replace with property
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

    def get_filename(self) -> Path:  # TODO: replace with property
        if hasattr(self, "filename"):
            return self.filename
        title = self.get_title()
        filename = Path(f"{title}.md")
        return filename

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
