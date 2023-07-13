#!/usr/bin/env python3
import logging as log
from pathlib import Path
from typing import Generator, TextIO

import pandoc
import requests
from pandoc.types import Link, Pandoc
from rich import print
from urllib.parse import ParseResult, urlparse, urljoin


def download(url) -> str:
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
        url: ParseResult = urlparse(target[0])
        text: str = pandoc.write(inline).strip()

        if url.netloc != DOMAIN:
            continue

        pad_id: str = url.path.strip("/")
        html_link: str = pandoc.write(link_obj).strip()
        obsidian_link: str = f"[[{pad_id}.md|{text}]]"

        log.info(f"replaced {html_link!r} with {obsidian_link!r}")

        pad_content = pad_content.replace(html_link, obsidian_link)
    return pad_content


def clean_url(url: ParseResult) -> str:
    return urljoin(url.geturl(), url.path)


log.basicConfig(filename=f"{__file__}.log", filemode="w", level=log.INFO)

DOMAIN: str = "md.chaosdorf.de"
START_URL: str = f"https://{DOMAIN}/navigation"

# setting up working directory
WORKING_DIR: Path = Path("/home/dodo/chaosdorf_vault")
WORKING_DIR.mkdir(exist_ok=True)

to_check: set[str] = set()
checked: set[str] = set()

to_check.add(START_URL)

while to_check:
    current_url: str = to_check.pop()
    current_pad: str = download(current_url)
    pad_id: str = urlparse(current_url).path.strip("/")

    log.info(f"{current_url=}")

    links: list[ParseResult] = get_intern_links(current_pad)
    log.info(f"{len(links)} link objects were found")

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
