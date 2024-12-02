#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
from core.base_parser import BaseBlogParser
from core.log_utils import logger

class YuqueParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "语雀"
        self.platform_flag = "yuque"

        # 设置语雀特定的选择器
        self.selectors.update({
            'title': [
                ('h1', {'id': 'article-title'}),
            ],
            'content': [
                ('article', {'class': 'article-content'}),
            ],
            'author': [
                ('a', {'class_': 'index-module_popover'}),
            ],
            'date': [
                ('span', {'class': 'item-text'}),
            ],
        })