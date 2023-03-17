import logging
from pathlib import Path

from medusa.converter import Converter
from medusa.crawler import Crawler

logging.basicConfig(filename="crawler.log", filemode="w", level=logging.DEBUG)

root = r"https://md.chaosdorf.de"
start = "navigation"

pad_dir: Path = Path.cwd() / Path("pads")
vault_dir: Path = Path.cwd() / Path("obsidian_vault")

crawler = Crawler(root, pad_dir)
pads = crawler.crawl(start)

for pad in pads:
    crawler.download(pad)

converter = Converter(root, pad_dir, vault_dir)
converter.convert()
