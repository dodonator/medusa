from urllib.parse import urljoin, urlparse

import pandoc
from pandoc.types import Link


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


class PadLink:
    raw: str
    url: str
    text: str
    pad_id: str

    def __init__(self, link_obj: Link):
        # Link(Attr, [Inline], Target)
        _, inline, target = link_obj
        self.raw = pandoc.write(link_obj).strip()
        self.url = clean_url(target[0])
        self.text = pandoc.write(inline).strip()
        self.pad_id = pad_id_from_url(self.url)

    def __repr__(self) -> str:
        return f"PadLink(text='{self.text}',url='{self.url}')"
