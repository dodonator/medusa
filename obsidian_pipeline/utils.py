import hashlib
from pathlib import Path
from typing import Generator
from urllib.parse import urljoin, urlparse

import pandoc
import requests
from pandoc.types import Link, Pandoc

DL: str = "download"


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


def get_pad_title(url: str) -> str:
    """Returns title of HedgeDoc Pad.

    Args:
        url (str): url to the pad

    Returns:
        str: pad title
    """
    response = requests.get(url)
    doc: Pandoc = pandoc.read(response.text)
    meta: list = doc[0]
    meta_dict: dict = meta[0]
    title: str = pandoc.write(meta_dict.get("title")).strip()
    return title


def get_pad_tags(url: str) -> set[str]:
    return set()


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


def extract_urls(root: str, pad_id: str) -> list:
    """Extracts link urls from HedgeDoc Pad.

    Args:
        root (str): base url of HedgeDoc
        pad_id (str): id of the pad

    Returns:
        dict: result (pad_id:url)
    """
    doc: Pandoc = download_pad(root, pad_id)

    blocks = doc[1]
    links: Generator = (
        block for block in pandoc.iter(blocks) if isinstance(block, Link)
    )

    urls: list = []
    for link in links:
        link: Link
        target = link[2]  # Link(Attr, [Inline], Target)
        url: str = clean_url(target[0])
        if url.startswith(root):
            urls.append(url)

    return urls


def download_pad(root: str, pad_id: str) -> Pandoc:
    """Downloads pad from HedgeDoc and returns it as pandoc document.

    Args:
        root (str): base url of HedgeDoc
        pad_id (str): id of the pad

    Returns:
        Pandoc: pad as pandoc document
    """
    link_str: str = f"{root}/{pad_id}/{DL}"
    response = requests.get(link_str)

    doc: Pandoc = pandoc.read(response.text)
    return doc
