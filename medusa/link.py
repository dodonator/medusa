from urllib.parse import ParseResult, urljoin, urlparse

import pandoc
from pandoc.types import Link


class PadLink:
    raw: str
    clean: str
    root: str
    text: str
    pad_id: str

    def __init__(self, link_obj: Link):
        # Link(Attr, [Inline], Target)
        _, inline, target = link_obj

        self.raw = pandoc.write(link_obj).strip()
        url: ParseResult = urlparse(target[0])

        # remove queries and fragments
        clean_url = urljoin(url.geturl(), url.path)
        self.clean = clean_url

        self.root = url.netloc
        self.pad_id = url.path[1:]
        self.text = pandoc.write(inline).strip()

    def __repr__(self) -> str:
        return f"PadLink(text='{self.text}',url='{self.clean}')"
