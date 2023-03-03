from argparse import ArgumentParser
from typing import Generator

import pandoc
import requests
from pandoc.types import Link, Pandoc

DL: str = "download"

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
urls: set[str] = set()
for link in links:
    link: Link
    attr, inline, target = link
    link_text: str = pandoc.write(inline).strip()
    url: str = target[0]
    urls.add(url)
    # print(repr(link_text), url)

print(urls)
