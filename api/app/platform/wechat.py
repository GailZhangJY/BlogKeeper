#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
from core.base_parser import BaseBlogParser
from core.log_utils import logger

class WeChatParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "微信公众号"
        self.platform_flag = "wechat"
        
        # 更新选择器而不是完全重写
        self.selectors.update({
            'title': [
                ('h1', {'id': 'activity-name'}),
            ],
            'content': [
                ('div', {'id': 'js_content'}),
            ],
            'author': [
                ('a', {'id': 'js_name'}),
                ('strong', {'class': 'profile_nickname'}),
            ],
            'date': [
                ('em', {'id': 'publish_time'}),
            ]
        })