from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
import asyncio
import requests
from typing import List, Dict, Optional
from core.base_parser import BaseBlogParser
from urllib.parse import urlparse
from core.log_utils import logger

class CNBlogParser(BaseBlogParser):
    def __init__(self):
        super().__init__()  # 调用父类的初始化方法
        self.platform_name = "博客园"
        self.platform_flag = "cnblog"
        
        # 更新选择器而不是完全重写
        self.selectors.update({
            'title': [
                ('h1', {'class': 'postTitle'}),
                ('a', {'class': 'postTitle2 vertical-middle'})
            ],
            'author': [
                ('a', {'class': 'author_name'}),
                ('div', {'class': 'author_name'}),
                ('a', {'id': 'author_profile_detail_blog'}),
                ('a', {'class': 'headermaintitle'})
            ],
            'content': [
                ('div', {'id': 'cnblogs_post_body'}),
                ('div', {'class': 'blogpost-body'})
            ],
            'date': [
                ('span', {'id': 'post-date'}),
                ('span', {'id': 'post-date-text'})
            ],
            'tag': [
                ('div', {'class': 'PostListTitle'}),
                ('div', {'id': 'taglist_title'}),
                ('h1', {'class': 'PostListTitle'}),
                ('div', {'class': 'catalog-title'}),
                ('div', {'class': 'headline'}),
                ('title', {}),
                ('div', {'class': 'tag-name'}),
                ('meta', {'name': 'keywords'})
            ]
        })

    def _parse_post_item(self, article) -> Dict:
        """解析单个文章项的信息"""
        try:
            # 获取标题和链接
            logger.debug("开始解析文章标题和链接...")
            title_elem = article.find('a', class_='vertical-middle')
            if not title_elem:
                title_elem = article.find('a')
            
            title = ''
            url = ''
            if title_elem:
                # 标题可能在span标签内
                title_span = title_elem.find('span')
                title = title_span.get_text(strip=True) if title_span else title_elem.get_text(strip=True)
                url = title_elem['href'] if 'href' in title_elem.attrs else ''
                logger.debug(f"找到标题: {title}")
                logger.debug(f"找到链接: {url}")
            
            # 获取作者和时间信息
            logger.debug("开始解析作者和时间信息...")
            desc = article.find('div', class_='postDesc2')
            author = ''
            time = ''
            if desc:
                desc_text = desc.get_text(strip=True)
                parts = desc_text.split(' ', 2)  # 分割成最多3部分
                if len(parts) >= 2:
                    author = parts[0]
                    time = parts[1]
                    logger.debug(f"找到作者: {author}")
                    logger.debug(f"找到时间: {time}")
            
            # 获取统计信息
            logger.debug("开始解析统计信息...")
            view_count = comment_count = digg_count = 0  # 默认值改为0（整数）
            
            view_span = article.find('span', class_='post-view-count')
            if view_span:
                try:
                    view_count = int(view_span.get_text(strip=True).split(':')[-1].strip())
                    logger.debug(f"阅读数: {view_count}")
                except (ValueError, IndexError):
                    logger.warning("无法解析阅读数，使用默认值0")
                    view_count = 0
                
            comment_span = article.find('span', class_='post-comment-count')
            if comment_span:
                try:
                    comment_count = int(comment_span.get_text(strip=True).split(':')[-1].strip())
                    logger.debug(f"评论数: {comment_count}")
                except (ValueError, IndexError):
                    logger.warning("无法解析评论数，使用默认值0")
                    comment_count = 0
            
            digg_span = article.find('span', class_='post-digg-count')
            if digg_span:
                try:
                    digg_count = int(digg_span.get_text(strip=True).split(':')[-1].strip())
                    logger.debug(f"推荐数: {digg_count}")
                except (ValueError, IndexError):
                    logger.warning("无法解析推荐数，使用默认值0")
                    digg_count = 0
            
            # 返回解析结果
            logger.debug("文章解析完成")
            return {
                'title': title,
                'url': url,
                'author': author,
                'time': time,
                'view_count': view_count,
                'comment_count': comment_count,
                'digg_count': digg_count
            }
            
        except Exception as e:
            logger.error(f"解析文章时出错: {str(e)}", exc_info=True)
            return None

    async def get_tag_posts(self, tag_url: str, max_pages: Optional[int] = None) -> List[Dict]:
        """获取标签页面下的所有文章"""
        all_posts = []
        page = 1
        
        while True:
            # 构建分页URL
            if page == 1:
                current_url = tag_url
            else:
                if tag_url.endswith('/'):
                    current_url = f"{tag_url}default.html?page={page}"
                else:
                    current_url = f"{tag_url}/default.html?page={page}"
            
            logger.debug(f"正在获取第 {page} 页...")
            try:
                response = requests.get(current_url)
                if response.status_code != 200:
                    logger.warning(f"获取页面失败: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                # 查找所有文章条目
                articles = soup.find_all('div', class_='PostList')
                
                if not articles:
                    logger.debug("没有找到更多文章")
                    break
                
                # 解析当前页的所有文章
                for article in articles:
                    post_info = self._parse_post_item(article)
                    if post_info['title'] and post_info['url']:  # 只添加有效的文章
                        all_posts.append(post_info)
                
                # 检查是否有下一页
                next_page = soup.find('a', string=re.compile(r'下一页'))
                if not next_page or (max_pages and page >= max_pages):
                    break
                
                page += 1
                # 添加延迟避免请求过快
                await asyncio.sleep(1)
            
            except Exception as e:
                logger.error(f"处理页面时出错: {str(e)}", exc_info=True)
                break
        
        return all_posts