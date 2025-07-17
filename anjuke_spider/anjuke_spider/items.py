# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AnjukeSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()        # 标题
    house_type = scrapy.Field()   # 户型
    area = scrapy.Field()         # 面积
    direction = scrapy.Field()    # 朝向
    floor = scrapy.Field()        # 楼层
    build_year = scrapy.Field()   # 建造年份
    community = scrapy.Field()    # 小区名称
    district = scrapy.Field()     # 区域
    address = scrapy.Field()      # 地址
    total_price = scrapy.Field()  # 总价
    unit_price = scrapy.Field()   # 单价
