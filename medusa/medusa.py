#!/usr/bin/env python3
import logging as log
from argparse import ArgumentParser
from pathlib import Path
from typing import Generator, TextIO
from urllib.parse import ParseResult, urljoin, urlparse

import pandoc
import requests
from pandoc.types import Link, Pandoc

log.basicConfig(filename=f"{Path(__file__).stem}.log", filemode="w", level=log.INFO)


def download(url: str) -> str:
    """Downloads pad content from url.

    Args:
        url (str): url to pad

    Raises:
        Exception: http status code

    Returns:
        str: pad content
    """
    url = f"{url}/download"
    response: requests.models.Response = requests.get(url)
    status_code: int = response.status_code

    if status_code == 200:
        content: str = response.text
    else:
        log.error(f"Couldn't download pad {url}")
        raise Exception("Couldn't download pad {url}")
    return content


def extract_link_objects(pad_content: str) -> list[Link]:
    """Extracts all pandoc Link objects from markdown str.

    Args:
        pad_content (str): markdown str

    Returns:
        list[Link]: list of Link objects
    """
    doc: Pandoc = pandoc.read(pad_content)
    blocks: list = doc[1]

    # filters all link objects
    link_objects: list[Link] = [
        block for block in pandoc.iter(blocks) if isinstance(block, Link)
    ]
    return link_objects


def get_intern_links(pad_content: str) -> list[ParseResult]:
    links: list[ParseResult] = []
    link_obj: Link
    for link_obj in extract_link_objects(pad_content):
        target = link_obj[2]
        url: ParseResult = urlparse(target[0])
        if url.netloc != DOMAIN:
            log.info(f"{url} is an external url")
            continue
        links.append(url)
    return links


def substitute_links(pad_content: str) -> str:
    doc: Pandoc = pandoc.read(pad_content)
    blocks: list = doc[1]

    # filters all link objects
    link_objects: Generator = (
        block for block in pandoc.iter(blocks) if isinstance(block, Link)
    )

    link_obj: Link
    for link_obj in link_objects:
        _, inline, target = link_obj
        url_str: str = target[0]
        url: ParseResult = urlparse(url_str)
        text: str = pandoc.write(inline).strip()

        if url.netloc != DOMAIN:
            continue

        pad_id: str = url.path.strip("/")
        html_link: str = f"[{text}]({url_str})"
        obsidian_link: str = f"[[{pad_id}.md|{text}]]"

        log.info(f"replaced {html_link!r} with {obsidian_link!r}")

        pad_content = pad_content.replace(html_link, obsidian_link)
    return pad_content


def clean_url(url: ParseResult) -> str:
    return urljoin(url.geturl(), url.path)


def main(start: str) -> None:
    to_check: set[str] = set()
    checked: set[str] = set()

    to_check.add(start)

    while to_check:
        current_url: str = to_check.pop()
        current_pad: str = download(current_url)
        pad_id: str = urlparse(current_url).path.strip("/")

        log.info(f"{pad_id=}")

        links: list[ParseResult] = get_intern_links(current_pad)
        log.info(f"{len(links)} link objects were found")

        print(f"found {len(links):>3} links in {pad_id!r}")

        # clean links (remove fragments)
        cleaned_links: list[str] = list(map(clean_url, links))

        link: str
        for link in cleaned_links:
            if link == current_url:
                # ignore circular links
                log.info(f"ignored {link} (circular)")
                continue

            to_check.add(link)
        checked.add(current_url)

        filename: str = f"{pad_id}.md"
        filepath: Path = WORKING_DIR / Path(filename)

        log.info(f"save pad @ {filepath}")

        # substitute html link with obsidian syntax
        substituted_pad = substitute_links(current_pad)

        # write to FS
        stream: TextIO
        with filepath.open("w", encoding="UTF-8") as stream:
            stream.write(substituted_pad)


if __name__ == "__main__":
    # create ArgumentParser
    parser: ArgumentParser = ArgumentParser(
        prog="medusa",
        description="create local obsidian vault from your HedgeDoc pads",
    )

    # add arguments
    parser.add_argument("start_url", type=str, help="start url")
    parser.add_argument("-p", "--path", type=Path, help="vault path")

    # parse args
    args = parser.parse_args()

    # setting up working directory
    WORKING_DIR: Path = args.path
    WORKING_DIR.mkdir(exist_ok=True)

    start: str = args.start_url
    start_url: ParseResult = urlparse(start)
    DOMAIN: str = start_url.netloc
    main(start)
