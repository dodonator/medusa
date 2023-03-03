from argparse import ArgumentParser
from typing import Generator
from urllib.parse import urljoin, urlparse

import pandoc
import requests
from pandoc.types import Link, Pandoc

DL: str = "download"


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


parser = ArgumentParser(description="Crawls the HedgeDoc.")
parser.add_argument("root", help="hegdedoc base url")
parser.add_argument(
    "-s", "--start", required=False, default="navigation", help="start pad"
)

args = parser.parse_args()
root = args.root
name = args.start

link_str: str = f"{root}/{name}/{DL}"
response = requests.get(link_str)

doc: Pandoc = pandoc.read(response.text)

blocks = doc[1]
links: Generator = (block for block in pandoc.iter(blocks) if isinstance(block, Link))

# list all links
urls: dict = {}
for link in links:
    link: Link
    target = link[2]  # Link(Attr, [Inline], Target)
    url: str = clean_url(target[0])
    pad_name = urlparse(url).path[1:]
    urls[pad_name] = url
print(urls)
