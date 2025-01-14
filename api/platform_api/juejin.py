#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Placeholder for Juejin parsing logic
from core.base_parser import BaseBlogParser
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from core.log_utils import logger

class JuejinParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "掘金"
        self.platform_flag = "juejin"
        
        # 设置掘金特定的选择器
        self.selectors.update({
            'title': [
                ('h1', {'class': 'article-title'}),
            ],
            'content': [
                ('div', {'id': 'article-root'}),
            ],
            'author': [
                ('span', {'class': 'name'}),
            ],
            'date': [
                ('time', {'class': 'time'}),
            ],
            'tag': [
                ('div', {'class': 'tag-list-box'}),
            ]
        })
        
        # 设置请求头
        self._headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://juejin.cn',
            'Referer': 'https://juejin.cn/',
        })