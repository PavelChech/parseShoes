import scrapy
import datetime
import processing_for_spider


class ShoesSpider(scrapy.Spider):
    name = 'Shoes'
    allowed_domains = ['www.wildberries.ru']
    start_urls = ['http://www.wildberries.ru']
    pages_count = 5

    def start_requests(self):
        for page in range(1, 1 + self.pages_count):
            url = f'https://www.wildberries.ru/catalog/muzhchinam/spetsodezhda/rabochaya-obuv?sort=popular&page={page}'
            yield scrapy.Request(url, callback=self.parse_pages)

    def parse_pages(self, response):
        for href in response.xpath("//a[contains(@class, 'ref_goods_n_p')]/@href").extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        timestamp = datetime.datetime.now().timestamp()
        RPC = response.xpath("//div[@class = 'article']/span/text()").extraxt_first()
        color = response.xpath("//span[@class = 'color']/text()").extraxt_first()
        url = response.url
        # title
        marketing_tags = processing_for_spider.clear_list_from_spaces(processing_for_spider.remove_empty_strs(
            response.xpath("//li[contains(@class,'about-advantages-item')]/text()").extract()))

        result = {
            "timestamp": timestamp,
            "RPC": RPC,
            "color": color,
            "url": url,
            "marketing_tags": marketing_tags
        }

        '''
                brand
                section
                price_data - currnt, orig, sale_tag
                stock
                assets
                metadata
                variants
                '''

        return result
