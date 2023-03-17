import hashlib
from pathlib import Path
from urllib.parse import urljoin, urlparse


def hash_file(path: Path):
    """Creates file checksum using md5.

    Args:
        path (Path): path to file

    Returns:
        hashlib._Hash: md5 checksum
    """
    BUF_SIZE = 256
    md5 = hashlib.md5()

    with path.open("rb") as stream:
        while True:
            data = stream.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

    return md5


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
