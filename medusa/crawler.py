#!/usr/bin/env python3
import logging as log
from pathlib import Path
from typing import Generator

import pandoc
import requests
from pandoc.types import Link, Pandoc
from utils import clean_url, pad_id_from_url


class Crawler:
    """Crawls for links in HedgeDoc Pads."""

    root: str
    output_dir: Path

    def __init__(self, root_url: str, output_dir: Path | None = None):
        self.root = root_url

        # sets up output directory
        if output_dir is None:
            self.output_dir = Path.cwd() / Path("output")
        else:
            self.output_dir = output_dir

        if not self.output_dir.exists():
            self.output_dir.mkdir()

    def get(self, pad_id: str, force_download: bool = False) -> str:
        """Gets pad content. Either from local copy or from remote source.

        Args:
            pad_id (str): pad id, either a phrase or a base64 hash
            force_download (bool, optional): wether local copies should be ignored. Defaults to False.

        Returns:
            str: content of the pad
        """
        text: str
        filename: str = f"{pad_id}.md"
        path: Path = self.output_dir / Path(filename)

        # tries to load pad from local copy
        if path.exists() and not force_download:
            log.info(f"reading pad {pad_id!r} from file {path}")
            with path.open("r", encoding="UTF-8") as stream:
                text = stream.read()

        else:
            # loads pad from hedgedoc
            pad_url: str = f"{self.root}/{pad_id}/download"
            log.info(f"reading pad {pad_id!r} from file {pad_url}")

            response: requests.models.Response = requests.get(pad_url)
            status_code: int = response.status_code

            log.info(f"got {status_code} from {pad_url}")

            if status_code == 200:
                text = response.text
            else:
                log.info(f"Couldn't download pad {pad_url}")
                text = ""
        return text

    def extract(self, pad_content: str) -> list[str]:
        """Returns list of pad ids linked in the pad.

        Args:
            pad_content (str): content of pad

        Returns:
            list[str]: list of pad ids
        """
        doc: Pandoc = pandoc.read(pad_content)
        blocks: list = doc[1]

        # filters all link objects
        link_objects: Generator = (
            block for block in pandoc.iter(blocks) if isinstance(block, Link)
        )

        linked_pads: list = []
        link: Link
        for link in link_objects:
            target: str = link[2]  # Link(Attr, [Inline], Target)

            # removes queries from url
            url: str = clean_url(target[0])

            if url.startswith(self.root):
                log.info(f"found link: {url}")
                pad_id: str = pad_id_from_url(url)

                linked_pads.append(pad_id)

        return linked_pads

    def crawl(self, start_pad: str) -> set[str]:
        """Starts with pad and does a breadth-first search for linked pads.

        Args:
            start_pad (str): pad to start from

        Returns:
            set[str]: set of pad ids
        """
        to_check: set[str] = set((start_pad,))  # set of pad ids to check
        checked: set[str] = set()  # set of already checked pad ids

        while to_check:
            # get an pad
            current_pad: str = to_check.pop()  # pad id to work on
            log.info(f"looking for links in {current_pad}")

            # download pad
            text: str = self.get(current_pad)  # content of the pad

            # extract links to other pads
            new_pads: set[str] = set(self.extract(text)) - checked
            log.info(f"found {len(new_pads)} pads in {current_pad}")

            # add new pads to queue
            to_check.update(new_pads)
            checked.add(current_pad)

        return checked

    def download(self, pad_id):
        """Gets a pad content and saves it.

        Args:
            pad_id (_type_): pad id
        """
        # content of the pad
        text: str = self.get(pad_id, force_download=True)

        filename: str = f"{pad_id}.md"
        filepath: Path = self.output_dir / Path(filename)
        log.info(f"downloading {pad_id} into {filepath}")

        with filepath.open("w", encoding="UTF-8") as stream:
            stream.write(text)
