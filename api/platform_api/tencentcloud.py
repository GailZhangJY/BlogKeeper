#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Placeholder for Juejin parsing logic
from core.base_parser import BaseBlogParser
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from core.log_utils import logger

class TencentCloudParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "腾讯云开发者社区"
        self.platform_flag = "tencentcloud"
        
        # 设置腾讯云特定的选择器
        self.selectors.update({
            'title': [
                ('h1', {'class': 'title-text'}),
            ],
            'content': [
                ('div', {'class': 'mod-content'}),
            ],
            'author': [
                ('div', {'class': 'mod-article-source__name'}),
            ],
            'date': [
                ('span', {'class': 'date-text'}),
            ],
        })