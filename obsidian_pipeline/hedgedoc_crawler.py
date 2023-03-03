from typing import Generator
import requests
import pandoc
from pandoc.types import Link
from rich import print as rich_print

link = "https://md.chaosdorf.de/navigation/download"
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
