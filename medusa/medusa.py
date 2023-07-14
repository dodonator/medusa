#!/usr/bin/env python3
import logging as log
from pathlib import Path
from typing import Generator, TextIO
from urllib.parse import ParseResult, urljoin, urlparse

import pandoc
import requests
from pandoc.types import Link, Pandoc

log.basicConfig(filename=f"{__file__}.log", filemode="w", level=log.DEBUG)

# setting up working directory
WORKING_DIR: Path = Path("/home/dodo/chaosdorf_vault")
WORKING_DIR.mkdir(exist_ok=True)


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
        content = response.text
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


def get_intern_links(pad_content: str):
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


def substitute_links(pad_content: str):
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


start: str = f"https://md.chaosdorf.de/navigation"
start_url: ParseResult = urlparse(start)
DOMAIN: str = start_url.netloc

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

    link: ParseResult
    for link in links:
        if clean_url(link) == current_url:
            # ignore circular links
            log.info(f"ignored {clean_url(link)} (circular)")
            continue

        to_check.add(clean_url(link))
    checked.add(current_url)

    filename: str = f"{pad_id}.md"
    filepath: Path = WORKING_DIR / Path(filename)

    log.info(f"save pad @ {filepath}")

    substituted_pad = substitute_links(current_pad)

    stream: TextIO
    with filepath.open("w", encoding="UTF-8") as stream:
        stream.write(substituted_pad)
