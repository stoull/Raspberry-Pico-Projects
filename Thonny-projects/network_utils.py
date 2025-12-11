"""
网络工具模块
提供 WiFi 连接和 NTP 时间同步功能
"""

import time
import network


class WiFiManager:
    """WiFi 连接管理器"""
    
    def __init__(self, ssid, password):
        """
        初始化 WiFi 管理器
        
        Args:
            ssid: WiFi 网络名称
            password: WiFi 密码
        """
        self.ssid = ssid
        self.password = password
        self.wlan = None
    
    def connect(self, timeout=30):
        """
        连接到 WiFi 网络
        
        Args:
            timeout: 连接超时时间（秒），默认 30 秒
            
        Returns:
            bool:  连接成功返回 True，失败返回 False
        """
        try:
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.config(pm=network.WLAN.PM_NONE)  # 禁用电源管理
            self.wlan.active(True)
            
            # 如果已经连接，直接返回
            if self.wlan.isconnected():
                print(f"已连接到 WiFi: {self.wlan.ifconfig()[0]}")
                return True
            
            # 开始连接
            print(f"正在连接到 WiFi: {self.ssid}")
            self.wlan.connect(self.ssid, self.password)
            
            # 等待连接
            start_time = time.time()
            while not self.wlan.isconnected():
                if time.time() - start_time > timeout:
                    print(f"WiFi 连接超时（{timeout}秒）")
                    return False
                
                print("等待连接...")
                time.sleep(1)
            
            # 连接成功
            ip_address = self.wlan.ifconfig()[0]
            print(f"WiFi 连接成功！IP 地址: {ip_address}")
            return True
            
        except Exception as e:
            print(f"WiFi 连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开 WiFi 连接"""
        if self.wlan and self.wlan.isconnected():
            self.wlan.disconnect()
            self.wlan.active(False)
            print("WiFi 已断开")
    
    def is_connected(self):
        """
        检查 WiFi 是否已连接
        
        Returns:
            bool: 已连接返回 True，否则返回 False
        """
        return self.wlan and self.wlan.isconnected()
    
    def get_ip_address(self):
        """
        获取 IP 地址
        
        Returns:
            str: IP 地址，未连接返回 None
        """
        if self.is_connected():
            return self.wlan.ifconfig()[0]
        return None
    
    def get_network_info(self):
        """
        获取网络信息
        
        Returns:
            dict: 包含 IP、子网掩码、网关、DNS 的字典
        """
        if self.is_connected():
            ifconfig = self.wlan.ifconfig()
            return {
                'ip': ifconfig[0],
                'subnet':  ifconfig[1],
                'gateway': ifconfig[2],
                'dns': ifconfig[3]
            }
        return None


class NTPTimeSync:
    """NTP 时间同步管理器"""
    
    # 常用 NTP 服务器列表
    NTP_SERVERS = [
        "ntp.aliyun.com",       # 阿里云
        "ntp.ntsc.ac.cn",       # 中国国家授时中心
        "ntp1.aliyun.com",      # 阿里云备用
        "pool.ntp.org",         # 国际 NTP 池
    ]
    
    def __init__(self, timezone_offset=8):
        """
        初始化 NTP 时间同步器
        
        Args:
            timezone_offset: 时区偏移量（小时），默认 8（北京时间 UTC+8）
        """
        self.timezone_offset = timezone_offset
    
    def sync(self, ntp_server=None, retry_count=3):
        """
        从 NTP 服务器同步时间
        
        Args:
            ntp_server:  NTP 服务器地址，默认使用服务器列表
            retry_count: 重试次数，默认 3 次
            
        Returns: 
            bool: 同步成功返回 True，失败返回 False
        """
        try:
            import ntptime
            from machine import RTC
            
            # 确定要使用的 NTP 服务器
            servers = [ntp_server] if ntp_server else self.NTP_SERVERS
            
            # 尝试每个服务器
            for server in servers:
                for attempt in range(retry_count):
                    try:
                        print(f"正在从 {server} 同步时间...  (尝试 {attempt + 1}/{retry_count})")
                        ntptime.host = server
                        ntptime.settime()
                        
                        # 同步成功，调整时区
                        self._adjust_timezone()
                        
                        current_time = self. get_iso8601_time()
                        print(f"时间同步成功: {current_time}")
                        return True
                        
                    except Exception as e: 
                        print(f"同步失败: {e}")
                        if attempt < retry_count - 1:
                            time.sleep(2)  # 重试前等待
                        continue
            
            print("所有 NTP 服务器同步失败")
            return False
            
        except ImportError:
            print("错误:  ntptime 模块不可用")
            return False
        except Exception as e:
            print(f"时间同步异常: {e}")
            return False
    
    def _adjust_timezone(self):
        """调整系统时间到指定时区"""
        try: 
            from machine import RTC
            
            rtc = RTC()
            utc_timestamp = time.mktime(time.localtime())
            local_timestamp = utc_timestamp + self.timezone_offset * 3600
            local_time = time.localtime(local_timestamp)
            
            rtc.datetime((
                local_time[0],  # 年
                local_time[1],  # 月
                local_time[2],  # 日
                local_time[6],  # 星期
                local_time[3],  # 时
                local_time[4],  # 分
                local_time[5],  # 秒
                0               # 微秒
            ))
            
        except Exception as e:
            print(f"时区调整失败: {e}")
    
    @staticmethod
    def get_iso8601_time():
        """
        获取 ISO 8601 格式的当前时间字符串
        
        Returns:
            str: ISO 8601 格式时间 (YYYY-MM-DDTHH:MM:SS)
        """
        current_time = time.localtime()
        
        iso8601_time = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
            current_time[0],  # 年
            current_time[1],  # 月
            current_time[2],  # 日
            current_time[3],  # 时
            current_time[4],  # 分
            current_time[5]   # 秒
        )
        
        return iso8601_time
    
    @staticmethod
    def get_timestamp():
        """
        获取当前时间戳
        
        Returns:
            int:  Unix 时间戳
        """
        return time.mktime(time.localtime())
    
    @staticmethod
    def format_time(format_str="%Y-%m-%d %H:%M:%S"):
        """
        格式化当前时间
        
        Args:
            format_str: 时间格式字符串
            
        Returns:
            str: 格式化的时间字符串
        """
        current_time = time.localtime()
        
        # MicroPython 不支持 strftime，手动格式化
        formatted_time = format_str.replace("%Y", "{:04d}".format(current_time[0]))
        formatted_time = formatted_time.replace("%m", "{:02d}".format(current_time[1]))
        formatted_time = formatted_time.replace("%d", "{:02d}".format(current_time[2]))
        formatted_time = formatted_time.replace("%H", "{:02d}".format(current_time[3]))
        formatted_time = formatted_time.replace("%M", "{:02d}".format(current_time[4]))
        formatted_time = formatted_time.replace("%S", "{:02d}".format(current_time[5]))
        
        return formatted_time


# ==================== 便捷函数 ====================

def quick_connect_wifi(ssid, password, timeout=30):
    """
    快速连接 WiFi（便捷函数）
    
    Args:
        ssid:  WiFi 网络名称
        password: WiFi 密码
        timeout: 连接超时时间（秒）
        
    Returns:
        WiFiManager: WiFi 管理器实例，连接失败返回 None
    """
    wifi = WiFiManager(ssid, password)
    if wifi.connect(timeout):
        return wifi
    return None


def quick_sync_time(timezone_offset=8, ntp_server=None):
    """
    快速同步时间（便捷函数）
    
    Args: 
        timezone_offset: 时区偏移量（小时）
        ntp_server:  NTP 服务器地址
        
    Returns:
        bool: 同步成功返回 True，失败返回 False
    """
    ntp = NTPTimeSync(timezone_offset)
    return ntp.sync(ntp_server)