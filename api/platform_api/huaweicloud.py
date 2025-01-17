#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.base_parser import BaseBlogParser
from bs4 import BeautifulSoup
import re
from datetime import datetime
from core.log_utils import logger

class HuaWeiCloudParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "华为云开发者社区"
        self.platform_flag = "huaweicloud"
        
        # 设置简书特定的选择器
        self.selectors.update({
            'title': [
                ('h1', {'class': 'cloud-blog-detail-title'}),  # 文章标题
            ],
            'content': [
                ('div', {'class': 'cloud-blog-detail-content-wrap'}),  # 文章内容
            ],
            'author': [
                ('a', {'class': 'sub-content-username por-link-red'}),  # 作者名
            ],
            'date': [
                ('span', {'class': 'article-write-time isMb'}),  # 发布时间
            ],
        })

