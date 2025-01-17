#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.base_parser import BaseBlogParser
from bs4 import BeautifulSoup
import re
from datetime import datetime
from core.log_utils import logger

class AliyunDeveloperParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "阿里云开发者社区"
        self.platform_flag = "aliyundeveloper"
        
        # 设置阿里云特定的选择器
        self.selectors.update({
            'title': [
                ('h1', {'class': 'article-title'}),  # 文章标题
            ],
            'content': [
                ('div', {'class': 'article-content'}),  # 文章内容
            ],
            'author': [
                ('a', {'class': 'blog-info-from-item'}),  # 作者名
            ],
            'date': [
                ('span', {'class': 'article-info-time'}),  # 发布时间
            ],
        })

