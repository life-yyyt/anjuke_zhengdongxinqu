# Scrapy settings for anjuke_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "anjuke_spider"

SPIDER_MODULES = ["anjuke_spider.spiders"]
NEWSPIDER_MODULE = "anjuke_spider.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "anjuke_spider (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 12
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://zhengzhou.anjuke.com/sale/zhengdongxinqu/'
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "anjuke_spider.middlewares.AnjukeSpiderSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'anjuke_spider.middlewares.ProxyMiddleware': 350,
    'anjuke_spider.middlewares.RandomUserAgentMiddleware': 400,
    'anjuke_spider.middlewares.CustomRetryMiddleware': 450,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'anjuke_spider.pipelines.AnjukeSpiderPipeline': 300,
    'anjuke_spider.pipelines.JsonWriterPipeline': 800,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 25
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = True

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# 代理设置
PROXY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 403, 404, 429]

# 设置较短的超时时间
DOWNLOAD_TIMEOUT = 15

# 重试设置
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 403, 404, 429]

# 并发设置
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 10

# 随机下载延迟
RANDOMIZE_DOWNLOAD_DELAY = True

# 设置JSON输出格式
FEED_EXPORT_ENCODING = 'utf-8'
FEED_EXPORT_INDENT = 4

# 处理重定向
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 3

# 增加下载延迟以避免被封
DOWNLOAD_DELAY = 15

# 调整并发和延迟设置
CONCURRENT_REQUESTS = 1  # 降低并发，避免IP快速耗尽
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 15  # 适当延迟

# 减少重试次数，避免浪费IP
RETRY_TIMES = 3

# 设置更严格的超时时间
DOWNLOAD_TIMEOUT = 30
