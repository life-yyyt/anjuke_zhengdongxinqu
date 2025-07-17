import requests
import json
import time

class IPManager:
    def __init__(self):
        self.api_url = "http://api.91http.com/v1/get-ip"
        self.params = {
            'trade_no': 'B401641780472',
            'secret': 'KwCFQgYuEs2ohtu7',
            'num': 10,
            'protocol': 1,
            'format': 'json',
            'sep': 1,
            'filter': 1
        }
        self.ip_pool = []
        self.ip_times = {}  # 记录每个IP的获取时间
        self.last_fetch_time = 0
        self.fetch_interval = 180  # 3分钟间隔
        self.min_pool_size = 3
        self.remaining_balance = 500

    def is_ip_valid(self, ip):
        """检查IP是否在有效期内"""
        if ip not in self.ip_times:
            return False
        return time.time() - self.ip_times[ip] < 180  # 3分钟有效期

    def fetch_ips(self):
        """从API获取新IP"""
        try:
            response = requests.get(self.api_url, params=self.params)
            data = json.loads(response.text)
            
            if data['code'] == 0:
                # 清理过期IP
                current_time = time.time()
                self.ip_pool = [ip for ip in self.ip_pool if self.is_ip_valid(ip)]
                
                # 添加新IP
                new_ips = [f"http://{ip['ip']}:{ip['port']}" 
                          for ip in data['data']['proxy_list']]
                self.ip_pool.extend(new_ips)
                
                # 记录新IP的获取时间
                for ip in new_ips:
                    self.ip_times[ip] = current_time
                
                self.last_fetch_time = current_time
                self.remaining_balance = data['data']['surplus_quantity']
                print(f"成功获取 {len(new_ips)} 个IP，剩余IP数量: {self.remaining_balance}")
                return True
        except Exception as e:
            print(f"请求API失败: {str(e)}")
        return False

    def get_ip(self):
        """获取一个IP"""
        # 清理过期IP
        current_time = time.time()
        self.ip_pool = [ip for ip in self.ip_pool if current_time - self.ip_times.get(ip, 0) < 180]
        
        # 如果IP池太小，获取新IP
        if len(self.ip_pool) < self.min_pool_size:
            self.fetch_ips()
        
        # 返回未过期的IP
        valid_ips = [ip for ip in self.ip_pool if self.is_ip_valid(ip)]
        if valid_ips:
            ip = valid_ips[0]
            self.ip_pool.remove(ip)
            return ip
            
        return None

    def add_ip(self, ip):
        """将IP添加回池中（如果IP还在有效期内）"""
        if ip not in self.ip_pool and time.time() - self.last_fetch_time < 180:  # 3分钟内的IP才重用
            self.ip_pool.append(ip)

    def remove_ip(self, ip):
        """移除失效的IP"""
        if ip in self.ip_pool:
            self.ip_pool.remove(ip)
        if ip in self.ip_times:
            del self.ip_times[ip]
        print(f"移除IP: {ip}, 当前IP池大小: {len(self.ip_pool)}")

    def process_request(self, request, spider):
        proxy = self.get_ip()
        if proxy:
            request.meta['proxy'] = proxy
            request.meta['proxy_retry_count'] = 0
            request.meta['download_timeout'] = 20  # 与全局设置保持一致
            spider.logger.info(f'Using proxy: {proxy}') 