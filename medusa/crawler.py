#!/usr/bin/env python3
import logging as log

from medusa.model import Pad, PadLink

log.basicConfig(level=log.INFO)


def crawl(url: str) -> list[Pad]:
    start = Pad(url)

    to_check: set = set((start,))
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
    return found_pads


url = "https://md.chaosdorf.de/navigation"
pads = crawl(url)
