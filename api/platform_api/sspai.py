#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Placeholder for Juejin parsing logic
from core.base_parser import BaseBlogParser
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from core.log_utils import logger

class SSPaiParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "少数派"
        self.platform_flag = "sspai"
        
        # 设置少数派特定的选择器
        self.selectors.update({
            'title': [
                ('div', {'id': 'article-title'}),
            ],
            'content': [
                ('div', {'class': 'article-body'}),
            ],
            'author': [
                'xpath://div[@class="article-header-author"]/span/span/div/a/div/span',
            ],
            'date': [
                'xpath://div[@class="article-author"]/div[@class="timer"]',
            ],
        })

        # 设置请求头
        self._headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://sspai.com/',
            'Referer': 'https://sspai.com/',
        })

    def _extract_date(self, soup):
        """提取文章发布日期
        
        支持的格式：
        - HH:MM（今天）
        - 昨天 HH:MM
        - 前天 HH:MM
        - MM/DD HH:MM（今年）
        - YYYY/MM/DD HH:MM（具体年份）
        
        Returns:
            str: 文章发布日期，格式为 YYYY-MM-DD
        """
        date_element = self._extract_element(soup, self.selectors['date'])
        logger.info(f"原始日期文本：{date_element}")
        
        if not date_element:
            return datetime.now().strftime('%Y-%m-%d')
            
        try:
            now = datetime.now()
            date_str = date_element.strip()
            
            # 处理 "昨天" 和 "前天"
            if "昨天" in date_str:
                return (now.date().replace(day=now.day - 1)).strftime('%Y-%m-%d')
            elif "前天" in date_str:
                return (now.date().replace(day=now.day - 2)).strftime('%Y-%m-%d')
            
            # 处理完整的年月日时间格式（2024/12/23 08:47）
            match = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', date_str)
            if match:
                year, month, day = map(int, match.groups())
                return f"{year:04d}-{month:02d}-{day:02d}"
            
            # 处理月日时间格式（01/17 18:00）
            match = re.match(r'(\d{1,2})/(\d{1,2})', date_str)
            if match:
                month, day = map(int, match.groups())
                year = now.year
                # 如果解析出的日期在未来，说明是去年的日期
                if month > now.month or (month == now.month and day > now.day):
                    year -= 1
                return f"{year:04d}-{month:02d}-{day:02d}"
            
            # 处理纯时间格式（18:00），表示今天
            if re.match(r'\d{1,2}:\d{2}', date_str):
                return now.strftime('%Y-%m-%d')
            
            logger.warning(f"未知的日期格式: {date_str}")
            return now.strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.error(f"日期解析错误 {date_element}: {str(e)}")
            return datetime.now().strftime('%Y-%m-%d')