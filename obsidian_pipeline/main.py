import logging
from pathlib import Path

from obsidian_pipeline.converter import Converter
from obsidian_pipeline.crawler import Crawler

logging.basicConfig(filename="crawler.log", filemode="w", level=logging.DEBUG)

root = "https://md.chaosdorf.de"
start = "navigation"

pad_dir: Path = Path.cwd() / Path("pads")
vault_dir: Path = Path.cwd() / Path("obsidian_vault")

crawler = Crawler(root, pad_dir)
pads = crawler.crawl(start)

for pad in pads:
    crawler.download(pad)

converter = Converter(root, pad_dir, vault_dir)
converter.convert()
