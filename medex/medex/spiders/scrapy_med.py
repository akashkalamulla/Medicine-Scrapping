import scrapy


class ScrapyMedSpider(scrapy.Spider):
    name = "scrapy_med"
    allowed_domains = ["medex.com.bd"]
    start_urls = ["https://medex.com.bd/brands?page=1"]

    def parse(self, response):
        pass
