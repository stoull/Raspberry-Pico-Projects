"""
轻量级日志模块
适用于 Raspberry Pi Pico 等资源受限设备
"""

import time


class SimpleLogger:
    """简单日志记录器"""
    
    # 日志级别
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    
    LEVEL_NAMES = {
        DEBUG: "DEBUG",
        INFO:  "INFO",
        WARNING: "WARN",
        ERROR: "ERROR"
    }
    
    def __init__(self, filename, max_size=10240, level=INFO, use_timestamp=True):
        """
        初始化日志记录器
        
        Args:
            filename: 日志文件名
            max_size: 最大文件大小（字节），默认 10KB，超过后会清空
            level: 日志级别，默认 INFO
            use_timestamp: 是否添加时间戳，默认 True
        """
        self.filename = filename
        self.max_size = max_size
        self.level = level
        self.use_timestamp = use_timestamp
        self.file = None
        self._open_file()
    
    def _open_file(self):
        """打开日志文件"""
        try:
            # 检查文件大小
            try:
                import os
                file_size = os.stat(self.filename)[6]
                
                # 如果文件过大，清空重建
                if file_size > self.max_size:
                    self.file = open(self.filename, "w")
                    self._write_raw("=== 日志文件已重置 ===\n")
                else:
                    self.file = open(self.filename, "a")
            except OSError:
                # 文件不存在，创建新文件
                self.file = open(self.filename, "w")
                
        except Exception as e:
            print(f"无法打开日志文件:  {e}")
            self.file = None
    
    def _write_raw(self, message):
        """直接写入消息到文件"""
        if self.file:
            try:
                self.file.write(message)
                self.file.flush()
            except Exception as e:
                print(f"写入日志失败: {e}")
    
    def _get_timestamp(self):
        """获取简单的时间戳"""
        if not self.use_timestamp:
            return ""
        
        try:
            t = time.localtime()
            return "{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                t[1], t[2], t[3], t[4], t[5]  # MM-DD HH:MM:SS
            )
        except:
            return ""
    
    def _log(self, level, message):
        """内部日志方法"""
        if level < self.level:
            return
        
        # 构建日志消息
        parts = []
        
        # 添加时间戳
        timestamp = self._get_timestamp()
        if timestamp:
            parts. append(f"[{timestamp}]")
        
        # 添加级别
        parts.append(f"[{self.LEVEL_NAMES[level]}]")
        
        # 添加消息
        parts.append(str(message))
        
        log_line = " ".join(parts) + "\n"
        
        # 写入文件
        self._write_raw(log_line)
        
        # 同时输出到控制台（可选）
        print(log_line. rstrip())
    
    def debug(self, message):
        """记录 DEBUG 级别日志"""
        self._log(self.DEBUG, message)
    
    def info(self, message):
        """记录 INFO 级别日志"""
        self._log(self.INFO, message)
    
    def warning(self, message):
        """记录 WARNING 级别日志"""
        self._log(self.WARNING, message)
    
    def error(self, message):
        """记录 ERROR 级别日志"""
        self._log(self.ERROR, message)
    
    def close(self):
        """关闭日志文件"""
        if self.file:
            try:
                self.file.close()
            except:
                pass
            self.file = None
    
    def __del__(self):
        """析构时关闭文件"""
        self.close()


class MemoryLogger: 
    """内存日志记录器（不写文件，仅保存在内存中）"""
    
    def __init__(self, max_lines=50):
        """
        初始化内存日志记录器
        
        Args:
            max_lines: 最大保存行数，默认 50 行
        """
        self.max_lines = max_lines
        self.logs = []
    
    def log(self, message):
        """记录日志到内存"""
        # 添加时间戳
        try:
            t = time.localtime()
            timestamp = "{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                t[1], t[2], t[3], t[4], t[5]
            )
            log_line = f"[{timestamp}] {message}"
        except:
            log_line = str(message)
        
        self.logs.append(log_line)
        
        # 保持在最大行数限制内
        if len(self.logs) > self.max_lines:
            self.logs.pop(0)
        
        print(log_line)
    
    def get_logs(self, last_n=None):
        """
        获取日志
        
        Args:
            last_n: 获取最后 N 条，默认全部
            
        Returns:
            list: 日志列表
        """
        if last_n: 
            return self.logs[-last_n:]
        return self. logs. copy()
    
    def clear(self):
        """清空日志"""
        self.logs.clear()
    
    def save_to_file(self, filename):
        """
        保存日志到文件
        
        Args:
            filename: 文件名
        """
        try:
            with open(filename, "w") as f:
                for log in self.logs:
                    f.write(log + "\n")
            print(f"日志已保存到 {filename}")
            return True
        except Exception as e: 
            print(f"保存日志失败: {e}")
            return False


# ==================== 全局日志实例 ====================
_global_logger = None


def init_logger(filename="_log.txt", max_size=10240, level=SimpleLogger.INFO):
    """
    初始化全局日志记录器
    
    Args: 
        filename: 日志文件名
        max_size:  最大文件大小（字节）
        level: 日志级别
        
    Returns:
        SimpleLogger: 日志记录器实例
    """
    global _global_logger
    _global_logger = SimpleLogger(filename, max_size, level)
    return _global_logger


def get_logger():
    """
    获取全局日志记录器
    
    Returns: 
        SimpleLogger: 日志记录器实例，如果未初始化则返回 None
    """
    return _global_logger


def log_info(message):
    """记录 INFO 日志（便捷函数）"""
    if _global_logger:
        _global_logger.info(message)
    else:
        print(f"[INFO] {message}")


def log_error(message):
    """记录 ERROR 日志（便捷函数）"""
    if _global_logger:
        _global_logger.error(message)
    else:
        print(f"[ERROR] {message}")


def log_warning(message):
    """记录 WARNING 日志（便捷函数）"""
    if _global_logger:
        _global_logger.warning(message)
    else:
        print(f"[WARNING] {message}")


def log_debug(message):
    """记录 DEBUG 日志（便捷函数）"""
    if _global_logger: 
        _global_logger.debug(message)
    else:
        print(f"[DEBUG] {message}")