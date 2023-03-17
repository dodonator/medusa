import hashlib
import logging as log
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandoc
from pandoc.types import Pandoc, Header


def hash_file(path: Path):
    """Creates file checksum using md5.

    Args:
        path (Path): path to file

    Returns:
        hashlib._Hash: md5 checksum
    """
    BUF_SIZE = 256
    md5 = hashlib.md5()

    with path.open("rb") as stream:
        while True:
            data = stream.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

    return md5


def pad_id_from_url(url: str) -> str:
    """Returns pad_id from url.

    Args:
        url (str): url to the pad

    Returns:
        str: pad id
    """
    pad_id: str = urlparse(url).path[1:]
    return pad_id


def clean_url(url_str: str) -> str:
    """
    Removes queries from url.
    Args:
        url_str (str): url as str

    Returns:
        str: resulting url
    """
    url_without_queries = urljoin(url_str, urlparse(url_str).path)
    return url_without_queries


def get_title(pad_content: str) -> str:
    doc: Pandoc = pandoc.read(pad_content)
    meta: list = doc[0]
    meta_dict: dict = meta[0]
    title: str

    # tries to get title from meta data
    if "title" in meta_dict:
        title = pandoc.write(meta_dict.get("title")).strip()
        log.info(f"found title {title!r} in meta data")

    else:
        blocks: list = doc[1]
        header: list[Header] = [
            block for block in blocks if isinstance(block, Header) and block[0] == 1
        ]
        if header:
            # uses first h1 header as title
            title = pandoc.write(header[0]).strip()
            # TODO: clean title
            log.info(f"first header was {title!r}")
        else:
            title = ""
            log.info("no title found")

    return title
