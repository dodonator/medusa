from typing import Generator

import pandoc
import requests
from pandoc.types import Link
from rich import print as rich_print

root: str = "https://md.chaosdorf.de"
link: str = root + "/navigation/download"
r = requests.get(link)

doc = pandoc.read(r.text)

# rich_print(doc)

meta, blocks = doc
links: Generator = (block for block in pandoc.iter(blocks) if isinstance(block, Link))

# list all links
for link in links:
    link: Link
    attr, inline, target = link
    print(target)
