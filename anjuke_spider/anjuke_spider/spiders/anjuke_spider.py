import scrapy
from ..items import AnjukeSpiderItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError

class AnjukeSpider(scrapy.Spider):
    name = 'anjuke'
    allowed_domains = ['anjuke.com']
    start_urls = ['https://zhengzhou.anjuke.com/sale/zhengdongxinqu/']
    
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 5,
    }
    
    # 添加页面计数器
    def __init__(self, *args, **kwargs):
        super(AnjukeSpider, self).__init__(*args, **kwargs)
        self.page_count = 1
        self.max_pages = 50  # 修改为50页
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, 
                               callback=self.parse,
                               errback=self.errback_httpbin,
                               dont_filter=True,
                               meta={'page': 1})  # 添加页面信息
    
    def errback_httpbin(self, failure):
        """错误处理"""
        self.logger.error(f"Request failed: {failure.value}")
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error(f'HttpError on {response.url}')
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error(f'DNSLookupError on {request.url}')
        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error(f'TimeoutError on {request.url}')
    
    def parse(self, response):
        # 获取当前页码
        current_page = response.meta.get('page', 1)
        self.logger.info(f'正在爬取第 {current_page} 页')
        
        # 获取房源列表
        house_list = response.xpath('//*[@id="esfMain"]/section/section[3]/section[1]/section[2]/div')
        
        for house in house_list:
            item = AnjukeSpiderItem()
            
            # 提取标题
            item['title'] = house.xpath('.//h3[@class="property-content-title-name"]/text()').get()
            
            # 提取户型信息 - 修改选择器
            room_spans = house.xpath('.//p[contains(@class, "property-content-info-text property-content-info-attribute")]//span/text()').getall()
            item['house_type'] = ''.join(room_spans) if room_spans else ''
            
            # 提取面积 - 修改选择器
            area = house.xpath('.//p[contains(@class, "property-content-info-text")][2]/text()').get()
            item['area'] = area.strip() if area else ''
            
            # 提取朝向 - 修改选择器
            direction = house.xpath('.//p[contains(@class, "property-content-info-text")][3]/text()').get()
            item['direction'] = direction.strip() if direction else ''
            
            # 提取楼层 - 修改选择器
            floor = house.xpath('.//p[contains(@class, "property-content-info-text")][4]/text()').get()
            item['floor'] = floor.strip() if floor else ''
            
            # 提取建造年份 - 修改选择器
            year = house.xpath('.//p[contains(@class, "property-content-info-text")][contains(text(), "年建造")]/text()').get()
            item['build_year'] = year.strip() if year else ''
            
            # 提取小区名称
            community = house.xpath('.//p[@class="property-content-info-comm-name"]/text()').get()
            item['community'] = community.strip() if community else ''
            
            # 提取区域
            district = house.xpath('.//p[@class="property-content-info-comm-address"]/span[1]/text()').get()
            item['district'] = district.strip() if district else ''
            
            # 提取地址 - 修改选择器
            address_spans = house.xpath('.//p[@class="property-content-info-comm-address"]/span[position()>1]/text()').getall()
            item['address'] = ''.join([span.strip() for span in address_spans]) if address_spans else ''
            
            # 提取总价
            total_price = house.xpath('.//span[@class="property-price-total-num"]/text()').get()
            item['total_price'] = total_price + '万' if total_price else ''
            
            # 提取单价
            unit_price = house.xpath('.//p[@class="property-price-average"]/text()').get()
            item['unit_price'] = unit_price.strip() if unit_price else ''
            
            # 数据清洗
            for field in item.keys():
                if isinstance(item[field], str):
                    # 移除多余的空白字符
                    item[field] = ' '.join(item[field].split())
                    # 移除特殊字符
                    item[field] = item[field].replace('\n', '').replace('\r', '').replace('\t', '')
            
            self.logger.info(f'Scraped item: {item}')
            yield item
        
        # 处理翻页 - 修改翻页逻辑
        if current_page < self.max_pages:
            # 构造下一页URL
            next_page_url = f'https://zhengzhou.anjuke.com/sale/zhengdongxinqu/p{current_page + 1}/'
            self.logger.info(f'构造下一页链接: {next_page_url}')
            
            yield scrapy.Request(
                next_page_url,
                callback=self.parse,
                errback=self.errback_httpbin,
                dont_filter=True,
                meta={
                    'page': current_page + 1,
                    'dont_redirect': True,
                    'handle_httpstatus_list': [301, 302]
                }
            )
        else:
            self.logger.info('已达到最大页数限制')
