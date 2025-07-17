# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import random
import requests
import json
import logging
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import time
from .ip_manager import IPManager


class AnjukeSpiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class AnjukeSpiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ProxyMiddleware:
    def __init__(self):
        self.ip_manager = IPManager()
        self.failed_proxies = {}
        self.max_retries = 3

    def process_request(self, request, spider):
        proxy = self.ip_manager.get_ip()
        if proxy:
            request.meta['proxy'] = proxy
            request.meta['proxy_retry_count'] = 0
            request.meta['download_timeout'] = 30
            spider.logger.info(f'Using proxy: {proxy}')

    def process_response(self, request, response, spider):
        proxy = request.meta.get('proxy', None)
        if response.status in [200]:
            # 请求成功，可以考虑重用IP
            if proxy:
                self.ip_manager.add_ip(proxy)
        elif response.status in [403, 429] or '访问频率过快' in response.text:
            # 代理被封或失效
            if proxy:
                self.ip_manager.remove_ip(proxy)
        return response

    def process_exception(self, request, exception, spider):
        proxy = request.meta.get('proxy', None)
        if proxy:
            self.ip_manager.remove_ip(proxy)
            retry_count = request.meta.get('proxy_retry_count', 0)
            if retry_count < self.max_retries:
                retry_count += 1
                request.meta['proxy_retry_count'] = retry_count
                request.dont_filter = True
                return request


class RandomUserAgentMiddleware:
    # 用户代理列表
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)


class CustomRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            # 删除失效的代理
            if 'proxy' in request.meta:
                spider.logger.info(f'Removing failed proxy: {request.meta["proxy"]}')
                # 如果使用代理池，这里可以将失效代理从池中删除
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        # 处理代理异常
        if 'proxy' in request.meta:
            spider.logger.info(f'Proxy error: {request.meta["proxy"]}')
            # 如果使用代理池，这里可以将异常代理从池中删除
        return super().process_exception(request, exception, spider)
