import scrapy
import datetime
import re


class ShoesSpider(scrapy.Spider):
    name = 'Shoes'
    allowed_domains = ['www.wildberries.ru']
    start_urls = ['http://www.wildberries.ru']
    pages_count = 6
    cookie = {'__region': '64_75_4_38_30_33_70_1_22_31_66_40_71_69_80_48_68',
                  '__store': '119261_122252_122256_117673_122258_122259_121631_122466_122467_122495_122496_122498_122590_122591_122592_123816_123817_123818_123820_123821_123822_124093_124094_124095_124096_124097_124098_124099_124100_124101_124583_124584_125611_116433_6159_507_3158_117501_120762_119400_120602_6158_121709_2737_117986_1699_1733_686_117413_119070_118106_119781',
                  '__wbl': 'cityId%3D77%26regionId%3D77%26city%3D%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%26phone%3D84957755505%26latitude%3D55%2C7247%26longitude%3D37%2C7882',
                  'ncache': '119261_122252_122256_117673_122258_122259_121631_122466_122467_122495_122496_122498_122590_122591_122592_123816_123817_123818_123820_123821_123822_124093_124094_124095_124096_124097_124098_124099_124100_124101_124583_124584_125611_116433_6159_507_3158_117501_120762_119400_120602_6158_121709_2737_117986_1699_1733_686_117413_119070_118106_119781%3B64_75_4_38_30_33_70_1_22_31_66_40_71_69_80_48_68%3B1.0--%3B12_3_18_15_21%3B%3B0',
                  'route': '5a25b90133d5524bd16297bd4f3f280681faf08e'
                  }


    def start_requests(self):
        for page in range(1, 1 + self.pages_count):
            url = f'https://www.wildberries.ru/catalog/muzhchinam/spetsodezhda/rabochaya-obuv?sort=popular&page={page}'
            yield scrapy.Request(url, callback=self.parse_pages, dont_filter=True,
                                 cookies=self.cookie_msc,
                                 meta={'dont_merge_cookies': True})

    def parse_pages(self, response):
        for href in response.xpath("//a[contains(@class, 'ref_goods_n_p')]/@href").extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse, dont_filter=True,
                                 cookies=self.cookie_msc,
                                 meta={'dont_merge_cookies': True})

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
