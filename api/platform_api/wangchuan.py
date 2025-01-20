#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Placeholder for Juejin parsing logic
from core.base_parser import BaseBlogParser
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from core.log_utils import logger

class WangchuanParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "硅谷王川"
        self.platform_flag = "wangchuan"
        
        # 设置硅谷王川特定的选择器
        self.selectors.update({
            'title': [
                ('h1', {'class': 'entry-title'}),
            ],
            'content': [
                ('div', {'class': 'entry-content'}),
            ],
            'author': [
                ('span', {'class': 'entry-meta-author'}),
            ],
            'date': [
                'xpath://div[@class="article-meta"]/span',
            ],
        })

    def _extract_author(self, soup):
        return super()._extract_element(soup, self.selectors['author'], '王川')