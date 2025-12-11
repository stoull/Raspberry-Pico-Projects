"""
DHT22 温湿度传感器模块
提供温湿度数据读取功能
"""

import time
from machine import Pin
import dht


class DHT22Sensor:
    """DHT22 温湿度传感器类"""
    
    def __init__(self, data_pin, led_pin=None, logger=None):
        """
        初始化 DHT22 传感器
        
        Args:
            data_pin: 数据引脚编号
            led_pin: LED 引脚（可选），用于指示读取状态
            logger: 日志记录器（可选）
        """
        self.sensor = dht.DHT22(Pin(data_pin))
        self.led = Pin(led_pin, Pin.OUT) if led_pin else None
        self.logger = logger
        
        # 统计信息
        self.read_count = 0
        self.error_count = 0
        self.last_temperature = None
        self.last_humidity = None
        self.last_read_time = None
    
    def _log(self, message, is_error=False):
        """内部日志方法"""
        if self.logger:
            if is_error:
                self.logger.error(message)
            else:
                self.logger.info(message)
        else:
            print(message)
    
    def _led_on(self):
        """LED 指示灯开启"""
        if self.led:
            self.led.on()
    
    def _led_off(self):
        """LED 指示灯关闭"""
        if self.led:
            self.led.off()
    
    def read(self, retry_count=3, retry_delay=2):
        """
        读取温湿度数据
        
        Args:
            retry_count: 失败重试次数，默认 3 次
            retry_delay: 重试间隔（秒），默认 2 秒
            
        Returns: 
            tuple: (温度, 湿度) 或 None（失败时）
        """
        self.read_count += 1
        
        for attempt in range(retry_count):
            try:
                # 关闭 LED 表示正在读取
                self._led_off()
                
                # 读取传感器
                self.sensor.measure()
                temperature = self.sensor.temperature()
                humidity = self.sensor.humidity()
                
                # 数据验证
                if not self._validate_data(temperature, humidity):
                    raise ValueError(f"数据超出正常范围:  温度={temperature}, 湿度={humidity}")
                
                # 保存最后读取的值
                self.last_temperature = temperature
                self.last_humidity = humidity
                self.last_read_time = time.time()
                
                # 开启 LED 表示读取成功
                self._led_on()
                
                self._log(f"读取成功: 温度={temperature}°C, 湿度={humidity}%")
                
                return (temperature, humidity)
                
            except Exception as e: 
                self.error_count += 1
                error_msg = f"读取失败 (尝试 {attempt + 1}/{retry_count}): {type(e).__name__} - {e}"
                
                # 最后一次尝试才记录错误
                if attempt == retry_count - 1:
                    self._log(error_msg, is_error=True)
                    self._led_off()
                    return None
                else:
                    self._log(error_msg)
                    time.sleep(retry_delay)
        
        return None
    
    def _validate_data(self, temperature, humidity):
        """
        验证传感器数据是否在合理范围内
        
        Args:
            temperature: 温度值
            humidity: 湿度值
            
        Returns:
            bool: 数据有效返回 True
        """
        # DHT22 测量范围:  温度 -40~80°C, 湿度 0~100%
        if temperature < -40 or temperature > 80:
            return False
        if humidity < 0 or humidity > 100:
            return False
        return True
    
    def read_fahrenheit(self, retry_count=3, retry_delay=2):
        """
        读取温度（华氏度）和湿度
        
        Args:
            retry_count: 失败重试次数
            retry_delay: 重试间隔（秒）
            
        Returns:
            tuple: (华氏温度, 湿度) 或 None
        """
        result = self.read(retry_count, retry_delay)
        if result: 
            celsius, humidity = result
            fahrenheit = (celsius * 9 / 5) + 32
            return (fahrenheit, humidity)
        return None
    
    def get_last_reading(self):
        """
        获取上次成功读取的数据
        
        Returns: 
            dict: 包含温度、湿度、时间的字典，如果没有则返回 None
        """
        if self.last_temperature is not None:
            return {
                'temperature': self.last_temperature,
                'humidity': self.last_humidity,
                'timestamp': self.last_read_time
            }
        return None
    
    def get_statistics(self):
        """
        获取统计信息
        
        Returns:
            dict: 读取次数、错误次数、成功率
        """
        success_count = self.read_count - self.error_count
        success_rate = (success_count / self.read_count * 100) if self.read_count > 0 else 0
        
        return {
            'total_reads': self.read_count,
            'errors': self.error_count,
            'success_rate': f"{success_rate:.1f}%"
        }
    
    def reset_statistics(self):
        """重置统计信息"""
        self.read_count = 0
        self.error_count = 0


# ==================== 兼容旧代码的简单函数 ====================

# 全局传感器实例（用于兼容旧代码）
_global_sensor = None


def init_sensor(data_pin=2, led_pin="LED", logger=None):
    """
    初始化全局传感器实例
    
    Args:
        data_pin: 数据引脚编号，默认 GPIO2
        led_pin: LED 引脚，默认板载 LED
        logger: 日志记录器
        
    Returns:
        DHT22Sensor:  传感器实例
    """
    global _global_sensor
    _global_sensor = DHT22Sensor(data_pin, led_pin, logger)
    return _global_sensor


def readDHT():
    """
    读取 DHT22 传感器（兼容旧代码的函数）
    
    Returns:
        tuple: (温度, 湿度) 或 None
    """
    if _global_sensor is None: 
        # 如果没有初始化，自动创建一个
        init_sensor()
    
    return _global_sensor.read()


def get_sensor():
    """
    获取全局传感器实例
    
    Returns:
        DHT22Sensor: 传感器实例
    """
    return _global_sensor