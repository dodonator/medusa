from crawler import Crawler
import logging

logging.basicConfig(filename="crawler.log", filemode="w", level=logging.DEBUG)

root = "https://md.chaosdorf.de"
start = "navigation"

crawler = Crawler(root)
pads = crawler.crawl(start)
print(pads)
for pad in pads:
    crawler.download(pad)
