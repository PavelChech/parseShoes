import scrapy


class ShoesSpider(scrapy.Spider):
    name = 'Shoes'
    allowed_domains = ['wildberries.ru']
    start_urls = ['http://wildberries.ru/']

    def parse(self, response):
        pass
