import json
from argparse import ArgumentParser
from typing import Generator
from urllib.parse import urljoin, urlparse

import pandoc
import requests
from pandoc.types import Link, Pandoc

DL: str = "download"


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


def extract_urls(root: str, pad_id: str) -> dict:
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

    urls: dict = {}
    for link in links:
        link: Link
        target = link[2]  # Link(Attr, [Inline], Target)
        url: str = clean_url(target[0])
        urls[pad_id] = url

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


parser = ArgumentParser(description="Crawls the HedgeDoc.")
parser.add_argument("root", help="HegdeDoc base url")
parser.add_argument(
    "-s", "--start", required=False, default="navigation", help="start pad"
)
parser.add_argument(
    "-o", "--output", required=False, default="urls.json", help="output file (json)"
)

args = parser.parse_args()
root = args.root
pad_id = args.start
output_file = args.output

urls = extract_urls(root, pad_id)
with open(output_file, "w", encoding="UTF-8") as stream:
    json.dump(urls, stream)
