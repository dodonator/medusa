#!/usr/bin/env python3
import logging as log
from pathlib import Path

from medusa.model import Pad, PadLink

log.basicConfig(level=log.INFO)

# setting up working directory
working_dir = Path("/home/dodo/chaosdorf_vault")
working_dir.mkdir(exist_ok=True)

# getting starting point
url = "https://md.chaosdorf.de/navigation"
nav = Pad(url)

to_check: set = set((nav,))
checked: set = set()

while to_check:
    pad: Pad = to_check.pop()  # get next pad

    log.info(f"starting extracting links from {pad}")
    links: list[PadLink] = pad.extract()

    pads: set[Pad] = set((p_link.pad for p_link in links))
    log.info(f"successfully extracted {len(pads)} links from {pad}")

    new_pads: set[Pad] = pads - checked
    to_check.update(new_pads)
    checked.add(pad)

found_pads: list[Pad] = list(checked)
