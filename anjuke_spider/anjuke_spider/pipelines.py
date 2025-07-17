# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
from datetime import datetime


class AnjukeSpiderPipeline:
    def process_item(self, item, spider):
        # 数据清洗和验证
        try:
            # 确保面积是数字
            if '㎡' in item['area']:
                item['area'] = item['area'].replace('㎡', '').strip()
            
            # 确保朝向数据正确
            if '层' in item['direction']:
                # 如果朝向字段包含楼层信息，交换数据
                item['direction'], item['floor'] = item['floor'], item['direction']
            
            # 确保建造年份格式正确
            if '年建造' in item['floor']:
                item['build_year'] = item['floor']
                item['floor'] = ''
            
            # 清理价格数据
            if item['unit_price']:
                item['unit_price'] = item['unit_price'].replace('元/㎡', '').strip()
            
            spider.logger.info(f'Processed item: {item}')
            
        except Exception as e:
            spider.logger.error(f'Error processing item: {str(e)}')
            
        return item


class JsonWriterPipeline:
    def __init__(self):
        # 使用当前时间戳创建文件名
        self.filename = f'anjuke_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        self.file = None
        self.items = []

    def open_spider(self, spider):
        self.file = open(self.filename, 'w', encoding='utf-8')
        # 写入JSON数组的开始符号
        self.file.write('[\n')
        self.first_item = True

    def close_spider(self, spider):
        if self.file:
            # 写入JSON数组的结束符号
            self.file.write('\n]')
            self.file.close()
            spider.logger.info(f'数据已保存到文件: {self.filename}')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False, indent=4)
        if not self.first_item:
            self.file.write(',\n')
        self.file.write(line)
        self.first_item = False
        return item
