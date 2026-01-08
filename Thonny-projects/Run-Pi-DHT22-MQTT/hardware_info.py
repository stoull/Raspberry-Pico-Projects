import machine
import sys
import os
import ubinascii
import time
import gc

def get_cpu_temperature():
    sensor = machine.ADC(4)
    voltage = sensor.read_u16() * (3.3 / 65535)
    temperature = 27 - (voltage - 0.706) / 0.001721
    return temperature

def print_memory_info():
    """打印详细的内存信息"""
    gc.collect()  # 执行垃圾回收
    
    mem_free = gc.mem_free()
    mem_alloc = gc. mem_alloc()
    mem_total = mem_free + mem_alloc
    
    print("\n【系统信息】")
    print(f"总内存:    {mem_total: >8} 字节 ({mem_total / 1024:>6.2f} KB)")
    print(f"已用内存:  {mem_alloc:>8} 字节 ({mem_alloc / 1024:>6.2f} KB)")
    print(f"剩余内存: {mem_free:>8} 字节 ({mem_free / 1024:>6.2f} KB)")
    print(f"使用率:    {(mem_alloc / mem_total * 100):>6.1f}%")
    
def print_hardware_info():
    print("=" * 50)
    print("Raspberry Pi Pico W 硬件信息")
    print("=" * 50)
    
    # 系统信息
    print("\n【系统信息】")
    print(f"平台: {sys.platform}")
    print(f"MicroPython 版本: {sys.version}")
    print(f"CPU 频率: {machine.freq() / 1_000_000:.0f} MHz")
    
    # 设备 ID
    print("\n【设备标识】")
    unique_id = ubinascii.hexlify(machine.unique_id()).decode()
    print(f"唯一 ID: {unique_id}")
    
    # 温度
    print("\n【传感器】")
    print(f"CPU 温度: {get_cpu_temperature():.2f}°C")
    
    # 存储信息
    print("\n【存储】")
    stat = os.statvfs('/')
    total = stat[0] * stat[2] / 1024
    free = stat[0] * stat[3] / 1024
    print(f"总空间: {total:.2f} KB")
    print(f"剩余空间: {free:.2f} KB")
    
    print("\n【电源】")
    reset_cause = machine.reset_cause()
    if reset_cause == machine.PWRON_RESET:
        cause_str = "上电复位"
    elif reset_cause == machine.WDT_RESET:
        cause_str = "看门狗复位"
    else:
        cause_str = f"其他 (代码: {reset_cause})"
    print(f"复位原因: {cause_str}")
    
    # 运行时间
    print(f"运行时间: {time.ticks_ms() / 1000:.2f} 秒")
    
    print_memory_info()
    
    print("=" * 50)

# 运行
# print_hardware_info()
"""
==================================================
Raspberry Pi Pico W 硬件信息
==================================================

【系统信息】
平台: rp2
MicroPython 版本: 3.4.0; MicroPython v1.23.0 on 2024-06-02
CPU 频率: 125 MHz

【设备标识】
唯一 ID: e6632c8593745230

【传感器】
CPU 温度: 28.45°C

【存储】
总空间: 848.00 KB
剩余空间: 668.00 KB

【电源】
复位原因: 上电复位
运行时间: 114.14 秒

【系统信息】
总内存:      191424 字节 (186.94 KB)
已用内存:     43808 字节 ( 42.78 KB)
剩余内存:   147616 字节 (144.16 KB)
使用率:      22.9%
==================================================
"""
