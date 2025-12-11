"""
DHT22 温湿度传感器数据采集并发送到 MQTT 服务器
运行环境:  Raspberry Pi Pico W (MicroPython)
功能: 每 5 分钟读取一次温湿度数据并通过 MQTT 发布
"""

import json
import time
from machine import Pin
from umqtt.simple import MQTTClient
from dht_sensor import readDHT
from network_utils import WiFiManager, NTPTimeSync


# ==================== 配置常量 ====================
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

# 日志文件
LOG_FILE = "_log.txt"


# ==================== 全局变量 ====================
led_pin = Pin("LED", Pin.OUT)
log_file = None
wifi_manager = None
time_sync = None


# ==================== 日志管理 ====================
def init_log_file():
    """初始化日志文件"""
    global log_file
    log_file = open(LOG_FILE, "w")
    start_time = f"程序启动时间: {time_sync.get_iso8601_time()}"
    write_log(start_time)


def write_log(message):
    """写入日志"""
    if log_file:
        timestamp = time_sync.get_iso8601_time() if time_sync else "----"
        log_file.write(f"[{timestamp}] {message}\n")
        log_file.flush()


# ==================== 网络初始化 ====================
def initialize_network():
    """初始化网络连接和时间同步"""
    global wifi_manager, time_sync
    
    # 创建 WiFi 管理器
    wifi_manager = WiFiManager(WIFI_SSID, WIFI_PASSWORD)
    
    # 连接 WiFi
    if not wifi_manager.connect():
        print("WiFi 连接失败，程序退出")
        return False
    
    # 创建时间同步器
    time_sync = NTPTimeSync(TIMEZONE_OFFSET)
    
    # 同步时间
    if not time_sync.sync():
        print("警告: 时间同步失败，将使用系统时间")
    
    return True


# ==================== MQTT 数据发布 ====================
def publish_sensor_data(mqtt_client):
    """读取传感器数据并发布到 MQTT"""
    temp_hum = readDHT()
    
    # 处理读取错误
    if isinstance(temp_hum, OSError):
        write_log(f"传感器读取错误: {temp_hum}")
        return False
    
    # 检查数据有效性
    if temp_hum is None:
        write_log("传感器返回 None")
        return False
    
    try:
        # 构造数据包
        data = {
            "created_at": time_sync.get_iso8601_time(),
            "temperature": temp_hum[0],
            "humidity":  temp_hum[1],
        }
        
        # 序列化为 JSON 并发布
        json_data = json.dumps(data)
        mqtt_client.publish(MQTT_TOPIC, json_data)
        
        print(f"数据已发布:  温度={temp_hum[0]}°C, 湿度={temp_hum[1]}%")
        return True
        
    except Exception as e:
        write_log(f"发布数据失败: {e}")
        return False


# ==================== 主循环 ====================
def start_main_loop():
    """主循环:  连接 MQTT 并定期发布传感器数据"""
    write_log("启动主循环")
    mqtt_client = None
    
    try:
        # 检查 WiFi 连接
        if not wifi_manager.is_connected():
            write_log("WiFi 断开，尝试重连...")
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
        print(f"已连接到 MQTT 服务器: {MQTT_HOST}:{MQTT_PORT}")
        write_log("MQTT 连接成功")
        
        # 主循环
        while True: 
            # 发布传感器数据
            publish_sensor_data(mqtt_client)
            
            # 等待下次采集
            write_log(f"等待 {SAMPLE_INTERVAL} 秒...")
            time.sleep(SAMPLE_INTERVAL)
            
    except KeyboardInterrupt:
        write_log("程序被用户中断")
        print("程序已停止")
        
    except Exception as e:
        error_msg = f"主循环异常: {type(e).__name__} - {e}"
        write_log(error_msg)
        print(error_msg)
        
    finally:
        # 清理资源
        if mqtt_client: 
            try:
                mqtt_client.disconnect()
                write_log("MQTT 已断开")
            except: 
                pass
        
        # 等待后重启循环
        print("6 秒后重启...")
        time.sleep(6)
        start_main_loop()


# ==================== 程序入口 ====================
def main():
    """程序主入口"""
    # 初始化网络连接
    if not initialize_network():
        return
    
    # 初始化日志
    init_log_file()
    
    # 点亮 LED 表示就绪
    led_pin.on()
    
    # 启动主循环
    start_main_loop()


# 启动程序
if __name__ == "__main__":
    main()