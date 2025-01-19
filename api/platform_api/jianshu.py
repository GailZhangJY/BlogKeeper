#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.base_parser import BaseBlogParser
from bs4 import BeautifulSoup
import re
from datetime import datetime
from core.log_utils import logger

class JianshuParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "简书"
        self.platform_flag = "jianshu"
        
        # 设置简书特定的选择器
        self.selectors.update({
            'title': [
                ('h1', {'class': '_1RuRku'}),  # 文章标题
            ],
            'content': [
                ('article', {'class': '_2rhmJa'}),  # 文章内容
            ],
            'author': [
                ('span', {'class': '_22gUMi'}),  # 作者名
                ('a', {'class': '_1OhGeD'}),  # 作者名
            ],
            'date': [
                ('time', {}),  # 发布时间
            ],
        })

