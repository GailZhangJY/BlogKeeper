#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
from core.base_parser import BaseBlogParser
from core.log_utils import logger
import time
import random

class RuanYiFengParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "阮一峰"
        self.platform_flag = "ruanyifeng"
        
        # 更新请求头，模拟真实浏览器访问
        self._headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'DNT': '1'
        })

        # 设置阮一峰特定的选择器
        self.selectors.update({
            'title': [
                ('h1', {'id': 'page-title'}),
            ],
            'content': [
                ('div', {'id': 'main-content'}),
            ],
            'author': [
                ('a', {'class': 'fn url'}),
            ],
            'date': [
                ('abbr', {'class': 'published'}),
            ],
        })

    def _init_session(self):
        """初始化会话，访问主页获取必要的cookies"""
        try:
            # 访问主页
            main_url = 'https://www.ruanyifeng.com/'
            self._headers['Referer'] = 'https://www.google.com/'
            response = self._session.get(main_url, headers=self._headers, timeout=30)
            response.raise_for_status()
            
            # 随机延迟
            time.sleep(random.uniform(1, 3))
            
            # 访问博客首页
            blog_url = 'https://www.ruanyifeng.com/blog/'
            self._headers['Referer'] = main_url
            response = self._session.get(blog_url, headers=self._headers, timeout=30)
            response.raise_for_status()
            
            logger.info("成功初始化会话和cookies")
            return True
        except Exception as e:
            logger.error(f"初始化会话失败: {str(e)}")
            return False

    def fetch_html(self, url: str) -> str:
        """重写获取页面HTML内容方法，确保正确的编码处理"""
        try:
            # 初始化会话
            if not self._init_session():
                return None
                
            # 设置文章页面的 Referer 为博客首页
            self._headers['Referer'] = 'https://www.ruanyifeng.com/blog/'
            
            # 添加随机延迟，避免频繁请求
            time.sleep(random.uniform(2, 4))
            
            # 打印当前的cookies
            logger.info(f"Current cookies: {dict(self._session.cookies)}")
            
            response = self._session.get(url, headers=self._headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            self.base_html = response.text
            return self.base_html
        except Exception as e:
            logger.error(f"获取页面失败: {str(e)}")
            return None

    def _extract_date(self, soup):
        """重写提取日期方法，处理特殊的日期格式
        Args:
            soup: BeautifulSoup对象
        Returns:
            str: 格式化的日期字符串
        """
        date_element = self._extract_element(soup, self.selectors['date'])
        if date_element:
            # 移除可能的HTML实体和特殊字符
            date_text = date_element.strip()
            # 使用正则提取年月日
            pattern = r'(\d{4}).*?(\d{1,2}).*?(\d{1,2})'
            match = re.search(pattern, date_text)
            if match:
                year, month, day = match.groups()
                return f"{year}-{int(month):02d}-{int(day):02d}"
        return None