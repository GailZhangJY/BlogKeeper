#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from core.base_parser import BaseBlogParser
from core.log_utils import logger
import requests
from urllib.parse import urlparse
import time
from core.config_utils import ConfigManager
import os

class ZhihuParser(BaseBlogParser):
    def __init__(self):
        super().__init__()
        self.platform_name = "知乎"
        self.platform_flag = "zhihu"
        
        self.config = ConfigManager()
        
        # 设置会话
        self._session = requests.Session()
        cookies = self.config.get_cookies(self.platform_flag)
        if cookies:
            self._session.cookies.update(cookies)
            logger.info("已加载知乎 cookies")

        # 设置知乎特定的选择器
        self.selectors.update({
            'title': [
                ('h1', {'class': 'Post-Title'}),  # 文章标题
            ],
            'content': [
                ('div', {'class': 'Post-Content'}),  # 文章内容
            ],
            'author': [
                ('span', {'class': 'author-name'}),  # 作者名
            ],
            'date': [
                ('span', {'class': 'post-time'}),  # 发布时间
            ],
        })


    def _api_get_blog(self, url):
        """获取页面内容，使用知乎 v4 API
        Args:
            url: 页面URL
        Returns:
            dict: 解析后的 JSON 数据
        """
        try:
            # 从 URL 中提取文章 ID
            post_id = url.split('/')[-1]
            logger.debug(f"提取的文章ID: {post_id}")
            
            # 获取 API URL
            api_url = self.config.get_endpoint(self.platform_flag, 'web_api', article_id=post_id)
            if not api_url:
                raise Exception("无法获取 API URL")
            
            logger.info(f"API URL: {api_url}")
            
            # 获取请求头和重试配置
            headers = self.config.get_headers(self.platform_flag)
            cookies = self.config.get_cookies(self.platform_flag)
            retry_times, retry_delay = self.config.get_retry_config()
            timeout = self.config.get_timeout()
            
            # 确保请求头包含必要的字段
            headers.update({
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Origin': 'https://zhuanlan.zhihu.com',
                'Referer': url,
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site'
            })
            
            # 不要在请求头中指定 Accept-Encoding，让 requests 自动处理
            if 'Accept-Encoding' in headers:
                del headers['Accept-Encoding']
            
            # 打印请求信息
            logger.debug("=== 请求信息 ===")
            logger.debug(f"Headers: {headers}")
            logger.debug(f"Cookies: {cookies}")
            logger.debug(f"Timeout: {timeout}")
            
            # 发送请求（带重试）
            response = None
            for i in range(retry_times):
                try:
                    response = self._session.get(
                        api_url, 
                        headers=headers, 
                        cookies=cookies,
                        timeout=timeout,
                        allow_redirects=True
                    )
                    
                    # 打印响应信息
                    logger.debug("=== 响应信息 ===")
                    logger.debug(f"Status Code: {response.status_code}")
                    logger.debug(f"Headers: {dict(response.headers)}")
                    logger.debug(f"Encoding: {response.encoding}")
                    logger.debug(f"Content-Type: {response.headers.get('content-type')}")
                    logger.debug(f"Content-Encoding: {response.headers.get('content-encoding')}")
                    
                    response.raise_for_status()
                    break
                except requests.RequestException as e:
                    logger.warning(f"请求失败 ({i + 1}/{retry_times}): {str(e)}")
                    if i == retry_times - 1:  # 最后一次重试
                        raise
                    time.sleep(retry_delay)
            
            # 检查响应内容类型
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                logger.warning(f"响应不是 JSON 格式: {content_type}")
                return None
            
            # 解析并返回 JSON 数据
            return response.json()
            
        except Exception as e:
            logger.error(f"获取页面内容失败: {str(e)}")
            return None

    def _get_blog_time(self, blog_info):
        try:
            # 提取文章时间
            created = blog_info.get('created', 0)  # 获取时间戳，如果不存在则默认为0
            if created:
                # 知乎时间戳可能是秒或毫秒
                if len(str(created)) > 10:  # 毫秒级时间戳
                    created = created / 1000
                time = datetime.fromtimestamp(created).strftime('%Y-%m-%d')
            else:
                time = datetime.now().strftime('%Y-%m-%d')
            logger.info(f"转换后的时间: {time}")
            return time
        except Exception as e:
            logger.error(f"获取时间失败: {str(e)}")

    def _get_blog_html(self, url):
        try:
            # 获取文章信息
            blog_info = self._api_get_blog(url)
            if not blog_info:
                raise Exception("无法获取文章信息")
            
            # 提取文章内容
            title = blog_info['title']
            author = blog_info['author']["name"]
            content = blog_info['content']
            time = self._get_blog_time(blog_info)
            
            # 格式化内容
            blog_html = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{title}</title>
            </head>
            <body> 
                <article>
                        <h1 class="Post-Title">{title}</h1>
                        <div class="Post-Author">
                            <span class="author-name">{author}</span>
                            <span class="post-time">{time}</span>
                        </div>
                        <div class="Post-Content">{content}</div>
                </article>
            </body>
            </html>
            """

            #logger.info("Blog HTML:\n" + blog_html)
            return blog_html
            
        except Exception as e:
            logger.error(f"下载知乎文章失败: {str(e)}")
            return False

    def fetch_html(self, url):
        """获取页面HTML内容
        Args:
            url: 页面URL
        Returns:
            str: HTML内容
        """
        try:
            self.base_html = self._get_blog_html(url)
            return self.base_html
        except Exception as e:
            logger.error(f"获取页面失败: {str(e)}")
            return None