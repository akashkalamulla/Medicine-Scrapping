import scrapy


class MedicineSpider(scrapy.Spider):
    name = "Medicine"
    allowed_domains = ["medex.com.bd"]
    start_urls = ["https://medex.com.bd/brands?page=1"]

    def parse(self, response):
        pass
