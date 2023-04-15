#!/usr/bin/env python3
import logging as log
from pathlib import Path
from typing import TextIO
from medusa.crawler import crawl
from medusa.model import Pad, PadLink

log.basicConfig(filename="medusa.log", filemode="w", level=log.WARNING)

# setting up working directory
working_dir = Path("/home/dodo/chaosdorf_vault")
working_dir.mkdir(exist_ok=True)

url = "https://md.chaosdorf.de/navigation"

# crawling for all linked pads
pads = crawl(url)

pad: Pad
for pad in pads:
    log.info(f"current pad: {pad}")

    content: str = pad.content

    links: list[PadLink] = pad.outgoing_links
    log.info(f"found {len(links)} outgoing links in {pad}")
    p_link: PadLink

    for p_link in links:
        old: str = p_link.raw
        if old not in content:
            log.error(f"Couldn't find {old} in {pad}")
            continue

        tmp_p = Pad(p_link.clean)
        obsidian_link: str = f"[[{tmp_p.title}|{p_link.text}]]"

        # replace markdown links with obsidian links
        log.info(f"replace all occurances of '{old}' with '{obsidian_link}'")
        content = content.replace(old, obsidian_link)

    # saving changed content
    filepath = working_dir / pad.filename
    stream: TextIO
    with filepath.open("w") as stream:
        stream.write(content)
