"""
DHT22 温湿度传感器数据采集并发送到 MQTT 服务器
运行环境:  Raspberry Pi Pico W (MicroPython)
功能: 每 5 分钟读取一次温湿度数据并通过 MQTT 发布
"""

import json
import time
from machine import Pin
from umqtt.simple import MQTTClient
from network_utils import WiFiManager, NTPTimeSync
from logger import init_logger, log_info, log_error, log_warning, get_logger
from dht_sensor import DHT22Sensor


# ==================== 配置常量 ====================
# 硬件配置
DHT22_PIN = 2           # DHT22 数据引脚
LED_PIN = "LED"         # 板载 LED

# WiFi 配置
WIFI_SSID = "******"
WIFI_PASSWORD = "******"

# MQTT 配置
MQTT_HOST = "192.168.1.157"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/dht22/2/data"
MQTT_USER = b"******"
MQTT_PASSWORD = b"******"
MQTT_CLIENT_ID = "WCwsVCBZa1xcSlRTUzwsaXkiUXlwOVVgKg"

# 时区配置
TIMEZONE_OFFSET = 8  # UTC+8 (北京时间)

# 数据采集间隔（秒）
SAMPLE_INTERVAL = 300

# 日志配置
LOG_FILE = "_log.txt"
LOG_MAX_SIZE = 10240  # 10KB


# ==================== 全局变量 ====================
led_pin = Pin(LED_PIN, Pin.OUT)
wifi_manager = None
time_sync = None
sensor = None


# ==================== 初始化模块 ====================
def initialize_logger():
    """初始化日志系统"""
    logger = init_logger(LOG_FILE, LOG_MAX_SIZE)
    log_info("=== 程序启动 ===")
    return logger


def initialize_network():
    """初始化网络连接和时间同步"""
    global wifi_manager, time_sync
    
    # 创建 WiFi 管理器
    wifi_manager = WiFiManager(WIFI_SSID, WIFI_PASSWORD)
    
    # 连接 WiFi
    if not wifi_manager.connect():
        log_error("WiFi 连接失败")
        return False
    
    # 创建时间同步器
    time_sync = NTPTimeSync(TIMEZONE_OFFSET)
    
    # 同步时间
    if not time_sync.sync():
        log_warning("时间同步失败，将使用系统时间")
    else:
        log_info(f"当前时间: {time_sync.get_iso8601_time()}")
    
    return True


def initialize_sensor():
    """初始化传感器"""
    global sensor
    
    logger = get_logger()
    sensor = DHT22Sensor(
        data_pin=DHT22_PIN,
        led_pin=LED_PIN,
        logger=logger
    )
    
    log_info("传感器初始化完成")
    return sensor


# ==================== MQTT 数据发布 ====================
def publish_sensor_data(mqtt_client):
    """读取传感器数据并发布到 MQTT"""
    # 读取传感器数据（自动重试 3 次）
    result = sensor.read(retry_count=3, retry_delay=2)
    
    if result is None:
        log_error("传感器读取失败")
        return False
    
    try:
        temperature, humidity = result
        
        # 构造数据包
        data = {
            "created_at": time_sync.get_iso8601_time(),
            "temperature": temperature,
            "humidity": humidity,
        }
        
        # 序列化为 JSON 并发布
        json_data = json.dumps(data)
        mqtt_client.publish(MQTT_TOPIC, json_data)
        
        log_info(f"数据已发布: 温度={temperature}°C, 湿度={humidity}%")
        return True
        
    except Exception as e:
        log_error(f"发布数据失败: {e}")
        return False


# ==================== 主循环 ====================
def start_main_loop():
    """主循环:  连接 MQTT 并定期发布传感器数据"""
    log_info("启动主循环")
    mqtt_client = None
    
    try:
        # 检查 WiFi 连接
        if not wifi_manager.is_connected():
            log_warning("WiFi 断开，尝试重连...")
            if not wifi_manager.connect():
                raise Exception("WiFi 重连失败")
        
        # 连接到 MQTT 服务器
        mqtt_client = MQTTClient(
            client_id=MQTT_CLIENT_ID,
            server=MQTT_HOST,
            port=MQTT_PORT,
            user=MQTT_USER,
            password=MQTT_PASSWORD
        )
        mqtt_client.connect()
        log_info(f"已连接到 MQTT 服务器: {MQTT_HOST}:{MQTT_PORT}")
        
        # 主循环
        loop_count = 0
        while True:
            loop_count += 1
            
            # 发布传感器数据
            publish_sensor_data(mqtt_client)
            
            # 每 10 次循环显示一次统计信息
            if loop_count % 10 == 0:
                stats = sensor.get_statistics()
                log_info(f"传感器统计:  {stats}")
            
            # 等待下次采集
            log_info(f"等待 {SAMPLE_INTERVAL} 秒...")
            time.sleep(SAMPLE_INTERVAL)
            
    except KeyboardInterrupt:
        log_info("程序被用户中断")
        print("程序已停止")
        
    except Exception as e:
        log_error(f"主循环异常: {type(e).__name__} - {e}")
        
    finally:
        # 清理资源
        if mqtt_client: 
            try:
                mqtt_client.disconnect()
                log_info("MQTT 已断开")
            except: 
                pass
        
        # 显示最终统计
        if sensor: 
            stats = sensor.get_statistics()
            log_info(f"最终统计: {stats}")
        
        # 等待后重启循环
        log_warning("6 秒后重启...")
        time.sleep(6)
        start_main_loop()


# ==================== 程序入口 ====================
def main():
    """程序主入口"""
    # 1. 初始化日志
    initialize_logger()
    
    # 2. 初始化网络连接
    if not initialize_network():
        log_error("网络初始化失败，程序退出")
        return
    
    # 3. 初始化传感器
    initialize_sensor()
    
    # 4. 点亮 LED 表示就绪
    led_pin.on()
    log_info("系统就绪")
    
    # 5. 启动主循环
    start_main_loop()


# 启动程序
if __name__ == "__main__":
    main()