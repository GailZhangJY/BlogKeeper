#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import os
from datetime import datetime
from colorama import init, Fore, Style

# 初始化colorama
init()

class ColoredFormatter(logging.Formatter):
    """自定义的彩色日志格式化器"""
    
    # 日志级别对应的颜色
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    # 不同类型消息的前缀图标
    ICONS = {
        'DEBUG': '🔍',
        'INFO': '✨',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '💥'
    }
    
    def format(self, record):
        # 获取对应的颜色
        color = self.COLORS.get(record.levelname, '')
        icon = self.ICONS.get(record.levelname, '')
        
        # 添加时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 格式化消息
        if record.levelname == 'INFO':
            # INFO级别的消息使用简洁格式
            formatted_message = f"{color}{icon} {record.getMessage()}{Style.RESET_ALL}"
        else:
            # 其他级别显示更详细的信息
            formatted_message = (
                f"{color}{icon} [{timestamp}] {record.levelname:<8} "
                f"{record.getMessage()} "
                f"({record.filename}:{record.lineno}){Style.RESET_ALL}"
            )
        
        return formatted_message

def setup_logger():
    """设置日志记录器"""
    # 创建logger
    logger = logging.getLogger('BlogParser')
    logger.setLevel(logging.DEBUG)  # 设置为最低级别，捕获所有日志
    
    # 如果logger已经有处理器，先清除
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # 控制台显示INFO及以上级别
    console_handler.setFormatter(ColoredFormatter())
    
    # 创建文件处理器
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'blog_parser_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # 文件记录DEBUG及以上级别
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # 添加处理器到logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 创建全局logger实例
logger = setup_logger()
