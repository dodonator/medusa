from dataclasses import dataclass

from medusa.utils import clean_url


@dataclass
class Link:
    url: str
    text: str

    def __init__(self, url: str, text: str):
        self.url = clean_url(url)
        self.text = text

    def to_markdown(self) -> str:
        return f"[{self.text}]({self.url})"
