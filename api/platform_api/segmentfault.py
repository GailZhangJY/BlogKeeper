#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.base_parser import BaseBlogParser
from bs4 import BeautifulSoup
import re
from datetime import datetime
from core.log_utils import logger

class SegmentfaultParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "思否"
        self.platform_flag = "segmentfault"
        
        # 设置简书特定的选择器
        self.selectors.update({
            'title': [
                ('h1', {'class': 'h2 mb-3'}),  # 文章标题
                ('a', {'class': 'link-dark'}),  # 文章标题
            ],
            'content': [
                #('div', {'class': 'mx-auto col-lg-7'}),  # 文章内容
                ('article', {'class': 'article fmt article-content'}),  # 文章内容
            ],
            'author': [
                ('strong', {'class': 'font-size-14'}),  # 作者名
            ],
            'date': [
                ('time', {'itemprop': 'datePublished'}),  # 发布时间
            ],
            'tag': [
                ('div', {'class': '_2Nttfz'}),  # 文章标签
            ]
        })

    def _extract_date(self, soup):
        """提取文章发布日期
        Args:
            soup: BeautifulSoup对象
        Returns:
            str: 文章发布日期，格式为 YYYY-MM-DD
        """
        from datetime import datetime
        
        date_element = self._extract_element(soup, self.selectors['date'])
        logger.info("原始日期文本：" + str(date_element))
        
        if not date_element:
            return ""
            
        date_text = str(date_element).strip()
        
        # 获取当前日期
        today = datetime.now()
        
        # 如果已经是YYYY-MM-DD格式，直接返回
        if re.match(r'\d{4}-\d{2}-\d{2}', date_text):
            return date_text
            
        # 处理中文日期格式（例如：1 月 8 日）
        match = re.search(r'(\d+)\s*月\s*(\d+)\s*日', date_text)
        if match:
            month = int(match.group(1))
            day = int(match.group(2))
            return f"{today.year}-{month:02d}-{day:02d}"
        
        # 处理"今天"和"刚刚"的情况
        date_text = today.strftime('%Y-%m-%d')
        return date_text
