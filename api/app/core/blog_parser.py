#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
from platform.cnblog import CNBlogParser
from platform.csdn import CSDNParser
from platform.zhihu import ZhihuParser
from platform.juejin import JuejinParser
from platform.jianshu import JianshuParser
from platform.wechat import WeChatParser
from platform.yuque import YuqueParser
from .log_utils import logger

class BlogParser:
    def __init__(self):
        """初始化博客解析器分发器"""
        self.parsers = {
            'cnblogs.com': CNBlogParser(),
            'blog.csdn.net': CSDNParser(),
            'zhuanlan.zhihu.com': ZhihuParser(),
            'juejin.cn': JuejinParser(),
            'jianshu.com': JianshuParser(),
            'mp.weixin.qq.com': WeChatParser(),
            #"yuque.com": YuqueParser(),
        }

    def get_parser(self, url: str):
        """根据URL获取对应的解析器
        Args:
            url: 博客文章URL
        Returns:
            Parser: 对应的解析器实例
        """
        domain = urlparse(url).netloc
        for key, parser in self.parsers.items():
            if key in domain:
                logger.info(f"使用 {parser.platform_name} 解析器")
                return parser
        logger.error(f"不支持的域名: {domain}")
        return None

    def parse(self, url: str, output_dir: str = None, save_options: dict = None) -> bool:
        """解析博客文章
        Args:
            url: 博客文章URL
            output_dir: 输出目录
            save_options: 保存选项
        Returns:
            bool: 是否成功
        """
        self.base_parser = self.get_parser(url)
        if not self.base_parser:
            return False
            
        return self.base_parser.parse_blog(url, output_dir, save_options)
        
    def get_file_list(self):
        return self.base_parser.get_file_list()

# 全局便捷函数
def parse_blog(url: str, save_options: dict = None, output_dir: str = None) -> bool:
    """解析单篇博客文章
    Args:
        url: 博客文章URL
        save_options: 保存选项
        output_dir: 输出目录
    Returns:
        bool: 解析成功返回True，失败返回False
    """
    parser = BlogParser()
    return parser.parse(url, output_dir, save_options)