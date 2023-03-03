from typing import Generator

import pandoc
import requests
from pandoc.types import Link
from rich import print as rich_print

root: str = "https://md.chaosdorf.de"
name: str = "navigation"
dw: str = "download"

link = f"{root}/{name}/{dw}"
response = requests.get(link)

doc = pandoc.read(response.text)

meta, blocks = doc
links: Generator = (block for block in pandoc.iter(blocks) if isinstance(block, Link))

# list all links
for link in links:
    link: Link
    attr, inline, target = link
    link_text: str = pandoc.write(inline).strip()
    url: str = target[0]
    print(repr(link_text), url)
