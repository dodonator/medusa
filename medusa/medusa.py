#!/usr/bin/env python3
"""
medusa - Get a local copy of your HedgeDoc, inside an obsidian vault.

Step 1: Download HedgeDoc Pad.
Step 2: Crawl the pad for all linked pads (links with same domain).
Step 3: Repeat Step 1 and 2 for each found pad.
Step 4: Rename filename to pad title (optional).
"""
import logging as log
from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path
from typing import Generator, TextIO
from urllib.parse import ParseResult, urljoin, urlparse

import pandoc
import requests
from pandoc.types import Link, Pandoc


class DownloadError(Exception):
    pass


log.basicConfig(
    filename=f"{Path(__file__).stem}.log", filemode="w", level=log.INFO
)


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
    response: requests.models.Response = requests.get(url, timeout=5)
    status_code: int = response.status_code

    if status_code == 200:
        content: str = response.text
    else:
        log.error("Couldn't download pad %s", url)
        raise DownloadError(f"Couldn't download pad {url}")
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
    """Reads all intern links from pad content.

    Args:
        pad_content (str): pad content

    Returns:
        list[ParseResult]: list of urls
    """
    links: list[ParseResult] = []
    link_obj: Link
    for link_obj in extract_link_objects(pad_content):
        target = link_obj[2]
        url: ParseResult = urlparse(target[0])
        if url.netloc != DOMAIN:
            log.info("%s is an external url", url)
            continue
        links.append(url)
    return links


def substitute_links(pad_content: str) -> str:
    """Substitutes markdown link syntax with obsidian link syntax.

    Args:
        pad_content (str): current pad content

    Returns:
        str: substituted content
    """
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

        log.info(
            "replaced %s with %s",
            repr(html_link),
            repr(obsidian_link),
        )

        pad_content = pad_content.replace(html_link, obsidian_link)
    return pad_content


def clean_url(url: ParseResult) -> str:
    """Cleans url.

    Removes Fragments and leaves only the path.

    Args:
        url (ParseResult): url to clean

    Returns:
        str: cleaned url
    """
    return urljoin(url.geturl(), url.path)


def rename_links(working_dir: Path):
    """Renames file to markdown title.

    Args:
        working_dir (Path): path to vault
    """
    translation_table: dict[Path, str] = {}

    file: Path
    for file in working_dir.glob("*.md"):
        # open file to get title
        stream: TextIO
        with file.open(mode="r") as stream:
            for line in stream:
                if "/" in line:
                    line = line.replace("/", "_")

                if line.startswith("# "):
                    title: str = line[2:].strip()
                    translation_table[file] = f"{title}.md"
                    print(f"found title {title!r} in {file.stem!r}")
                    continue

    for file, title in translation_table.items():
        content: str = file.read_text()

        for from_link, to_link in translation_table.items():
            content = content.replace(from_link.name, to_link)

        # save changed content
        file.write_text(content)

        # rename current file
        log.info("renamed %s to %s", file.name, title)
        file.rename(working_dir / Path(f"{title}"))


def crawl(root_url: str) -> None:
    """Start crawling for pad links.

    Args:
        root_url (str): start url
    """
    to_check: set[str] = set()
    checked: set[str] = set()

    to_check.add(root_url)

    while to_check:
        current_url: str = to_check.pop()
        current_pad: str = download(current_url)
        pad_id: str = urlparse(current_url).path.strip("/")

        log.info("pad_id: %s", pad_id)

        links: list[ParseResult] = get_intern_links(current_pad)
        log.info("%i link objects were found", len(links))

        print(f"found {len(links):>3} links in {pad_id!r}")

        # clean links (remove fragments)
        cleaned_links: list[str] = list(map(clean_url, links))

        link: str
        for link in cleaned_links:
            if link == current_url:
                # ignore circular links
                log.info("ignored %s (circular)", link)
                continue

            to_check.add(link)
        checked.add(current_url)

        filename: str = f"{pad_id}.md"
        filepath: Path = WORKING_DIR / Path(filename)

        log.info("save pad @ %s", filepath)

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
    parser.add_argument(
        "-p", "--path", type=Path, required=False, help="vault path"
    )
    parser.add_argument(
        "-r",
        "--rename",
        action=BooleanOptionalAction,
        required=False,
        default=True,
        help="wether files should be renamed",
    )

    # parse args
    args = parser.parse_args()

    # setting up working directory
    WORKING_DIR: Path = args.path
    WORKING_DIR.mkdir(exist_ok=True)

    start: str = args.start_url
    start_url: ParseResult = urlparse(start)
    DOMAIN: str = start_url.netloc
    crawl(start)

    if args.rename:
        # rename files and apply update links
        rename_links(WORKING_DIR)
