import scrapy
import datetime
import re


class ShoesSpider(scrapy.Spider):
    name = 'Shoes'
    allowed_domains = ['www.wildberries.ru']
    start_urls = ['http://www.wildberries.ru']
    pages_count = 6

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

        RPC = response.xpath("//div[@class = 'article']/span/text()").extract_first()

        color = response.xpath("//span[@class = 'color']/text()").extract_first()

        url = response.url

        title = ''.join(self.remove_empty_strs(response.xpath("//span[@class = 'name ']/text()").extract_first().split('/')[0]))
        if color:
            title = f"{title}, {color}"

        marketing_tags = self.remove_empty_strs(self.clear_list_from_spaces(
            response.xpath("//li[contains(@class,'about-advantages-item')]/text()").extract()))

        brand = response.xpath("//span[@class = 'brand']/text()").extract_first()

        section = self.remove_empty_strs(self.clear_list_from_spaces(
            response.xpath("//span[@class = 'name ']/text()").extract_first().split('/')[1:]))

        current_price = self.get_digits_from_str(response.xpath("//span[@class = 'final-cost']/text()").extract_first())
        original_price = self.get_digits_from_str(response.xpath("//del[@class = 'c-text-base']/text()").extract_first())
        sale_tag = ""
        if original_price:
            sale_tag = f"Скидка: {round(current_price / original_price * 100)}%"

        all_sizes = len(response.xpath("//div[contains(@class, 'size-list')]/label").extract())
        miss_sizes = len(response.xpath("//div[contains(@class, 'size-list')]/label[contains(@class, 'disabled')]").extract())
        in_stock =  miss_sizes < all_sizes

        main_image = response.xpath("//img[@class = 'preview-photo j-zoom-preview']/@src").extract_first()
        set_images = response.xpath("//span[@class = 'slider-content']/img/@src").extract()
        view = response.xpath("//span[@class = 'slider-content thumb_3d']/img/@src").extract_first()
        video =''

        description = response.xpath("//div[contains(@class, 'j-description collapsable-content description-text')]/p/text()").extract_first()

        keys = response.xpath("//div[contains(@class, 'pp')]/span/b/text()").extract()
        value = self.remove_empty_strs(self.clear_list_from_spaces(
            response.xpath("//div[contains(@class, 'pp')]/span/text()").extract()))
        metadata = {"Артикул": RPC, "Цвет": color}
        metadata.update({keys[i]:value[i] for i in range(len(keys))})


        variants = len(response.xpath("//li[contains(@class, 'color-v1')]/a").extract())

        result = {
            "timestamp": timestamp,
            "RPC": RPC,
            "color": color,
            "url": url,
            "title" : title,
            "marketing tags": marketing_tags,
            "brand": brand,
            "section": section,
            "price data": {"current": current_price,
                          "original": original_price,
                          "sale_tag": sale_tag},
            "stock":{"in stock": in_stock,
                     "count": 0},
            "assets": {"main image": main_image,
                       "set images": set_images,
                       "view360": view,
                       "video": video},
            "metadata": {"description": description,
                         "metadata": metadata},
            "variants": variants
        }
        yield result


    def get_digits_from_str(self, string):
        # Используем для выделения числа из цены
        digits = string.replace('\xa0', '')
        digits = float(re.search(r'\d+', digits).group(0))
        return digits


    def clear_list_from_spaces(self, other_list):
        # Очистить элементы (строки) списка от пробелов
        new_list = []
        [new_list.append(elem.replace('\n', '').strip()) for elem in other_list]
        return new_list


    def remove_empty_strs(self, other_list):
        new_list = []
        [new_list.append(string) for string in other_list if string]
        return new_list
