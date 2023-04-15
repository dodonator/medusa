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
    url: str
    root: str
    _content: str
    _filename: Path
    _title: str

    def __init__(self, url: str) -> None:
        self.url = url
        parse_result: ParseResult = urlparse(url)
        self.root = parse_result.netloc
        self.name = parse_result.path

    @property
    def content(self) -> str:
        if hasattr(self, "_content"):
            return self._content

        url = f"{self.url}/download"
        response: requests.models.Response = requests.get(url)
        status_code: int = response.status_code

        if status_code == 200:
            content = response.text
        else:
            log.error(f"Couldn't download pad {self.url}")
            raise Exception("Couldn't download pad {self.url}")
        self._content = content
        return content

    @property
    def title(self) -> str:
        if hasattr(self, "_title"):
            return self._title

        doc: Pandoc = pandoc.read(self.content)
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

        self._title = clean_title

        return self._title

    @property
    def filename(self) -> Path:
        if hasattr(self, "_filename"):
            return self._filename
        self._filename = Path(f"{self.title}.md")
        return self._filename

    def extract(self) -> list[PadLink]:
        doc: Pandoc = pandoc.read(self.content)
        blocks: list = doc[1]

        # filters all link objects
        link_objects: Generator = (
            block for block in pandoc.iter(blocks) if isinstance(block, Link)
        )

        links: list = []
        link_obj: Link
        for link_obj in link_objects:
            pad_link = PadLink(link_obj)

            if self.url == pad_link.clean:
                log.warning(f"circular import in pad {self.title}")
                continue

            if pad_link.root == self.root:
                log.info(f"found link: {pad_link}")
                links.append(pad_link)

        return links

    def __repr__(self) -> str:
        return f"Pad({self.title})"

    def __hash__(self) -> int:
        return hash(self.url)
