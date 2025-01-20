#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
from platform_api.cnblog import CNBlogParser
from platform_api.csdn import CSDNParser
from platform_api.zhihu import ZhihuParser
from platform_api.juejin import JuejinParser
from platform_api.jianshu import JianshuParser
from platform_api.wechat import WeChatParser
from platform_api.yuque import YuqueParser
from platform_api.segmentfault import SegmentfaultParser
from platform_api.ruanyifeng import RuanYiFengParser
from platform_api.tencentcloud import TencentCloudParser
from platform_api.huaweicloud import HuaWeiCloudParser
from platform_api.aliyundeveloper import AliyunDeveloperParser
from platform_api.toutiao import ToutiaoParser
from platform_api.wangchuan import WangchuanParser
from platform_api.sspai import SSPaiParser

from errors import PlatformError, ParseError
from .log_utils import logger

class BlogParser:
    def __init__(self):
        """初始化博客解析器分发器"""
        self.parsers = {
            'cnblogs.com': CNBlogParser(),
            'blog.csdn.net': CSDNParser(),
            #'zhuanlan.zhihu.com': ZhihuParser(),
            #'juejin.cn': JuejinParser(),
            'jianshu.com': JianshuParser(),
            'mp.weixin.qq.com': WeChatParser(),
            #"yuque.com": YuqueParser(),
            'segmentfault.com': SegmentfaultParser(),
            "ruanyifeng.com": RuanYiFengParser(),
            'cloud.tencent.com': TencentCloudParser(),
            #'bbs.huaweicloud.com': HuaWeiCloudParser(),
            #'developer.aliyun.com': AliyunDeveloperParser(),
            #'toutiao.com': ToutiaoParser(),
            'chuan.us': WangchuanParser(),
            #'sspai.com': SSPaiParser(),
        }

    def get_parser(self, url: str):
        """根据URL获取对应的解析器
        Args:
            url: 博客文章URL
        Returns:
            Parser: 对应的解析器实例
        Raises:
            PlatformError: 当域名不受支持时抛出
        """
        domain = urlparse(url).netloc
        for key, parser in self.parsers.items():
            if key in domain:
                logger.info(f"使用 {parser.platform_name} 解析器")
                return parser
        logger.error(f"不支持的域名:{domain}")
        raise Exception(f"不支持的域名：{domain}")

    def parse(self, url: str, output_dir: str = None, save_options: dict = None) -> bool:
        """解析博客文章
        Args:
            url: 博客文章URL
            output_dir: 输出目录
            save_options: 保存选项
        Returns:
            bool: 是否成功
        """
        try:
            self.base_parser = self.get_parser(url)
        except Exception as e:
            domain = urlparse(url).netloc
            supported_platforms = [parser.platform_name for parser in self.parsers.values()]
            raise PlatformError(
                domain=domain,
                supported_platforms=supported_platforms
            )

        try:
            success = self.base_parser.parse_blog(url, output_dir, save_options)
            return success
        except Exception as e:
            raise ParseError(str(e))
        
    def get_file_list(self):
        files = self.base_parser.get_file_list()
        if not files:
            raise ParseError("博客解析失败").to_http_exception()
        return files

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