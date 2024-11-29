from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
from core.base_parser import BaseBlogParser
from core.log_utils import logger

class CSDNParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "CSDN"
        self.platform_flag = "CSDN"
        
        # 更新选择器而不是完全重写
        self.selectors.update({
            'title': [
                ('div', {'class': 'article-title-box'}),
                ('h1', {'class': 'title-article'}),
            ],
            'author': [
                ('a', {'class': 'follow-nickName'}),
            ],
            'content': [
                ('div', {'id': 'article_content'}),
            ],
            'date': [
                ('span', {'class': 'time'}),
            ]
        })