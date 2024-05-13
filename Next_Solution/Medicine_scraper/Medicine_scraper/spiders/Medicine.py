import scrapy

class MedicineSpider(scrapy.Spider):
    name = "medex_spider"
    start_urls = [f"https://medex.com.bd/brands?page={page}" for page in range(1, 100, 10)]

    def parse(self, response):
        for product in response.css("div.product-box"):
            brand_name_elem = product.css(".col-xs-12.data-row-top::text").get()
            strength_elem = product.css(".grey-ligten::text").get()
            vitamin_info_elem = product.css(".col-xs-12::text").get()
            manufacturer_elem = product.css(".data-row-company::text").get()

            yield {
                "brand_name": brand_name_elem,
                "strength": strength_elem,
                "vitamin_info": vitamin_info_elem,
                "manufacturer": manufacturer_elem
            }