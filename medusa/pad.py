import logging as log
from pathlib import Path
from urllib.parse import urlparse

import requests


class Pad:
    name: str
    url: str
    root: str
    filename: Path
    content: str

    def __init__(self, url: str) -> None:
        self.url = url
        self.root = urlparse(url).netloc

    def get(self) -> str:
        if hasattr(self, "content"):
            return self.content

        url = f"{self.url}/download"
        response: requests.models.Response = requests.get(url)
        status_code: int = response.status_code

        if status_code == 200:
            text = response.text
        else:
            log.error(f"Couldn't download pad {self.url}")
            raise Exception("Couldn't download pad {self.url}")
        self.content = text
        return text
