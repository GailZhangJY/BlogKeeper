#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import requests
from datetime import datetime
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .save_utils import save_as_html, save_as_markdown, save_as_pdf, save_as_mhtml
from .log_utils import logger

class BaseBlogParser(ABC):
    def __init__(self):
        """初始化解析器"""
        self.platform_name = "Unknown"
        self.platform_flag = "Unknown"
        self._session = requests.Session()
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_html = None
        self.author = None
        self.time = None
        self.title = None
        self.content = None
        
        # 初始化保存处理器字典
        self.save_handlers = {
            'html': save_as_html,
            'pdf': save_as_pdf,
            'markdown': save_as_markdown,
            'mhtml': save_as_mhtml
        }
        
        self.selectors = {
            'author': [],
            'title': [],
            'content': [],
            'date': [],
        }
        
        # 保存解析后的文件列表
        self.file_list = []

    def get_file_list(self):
        """获取解析后的文件列表
        Returns:
            list: 包含文件信息的列表，每个元素是一个字典，包含：
                - title: 文件标题
                - download_url: 下载地址
                - size: 文件大小（字节）
                - format: 文件格式
        """
        return self.file_list

    def _add_file_to_list(self, file_path, file_name, format_type):
        """添加文件到文件列表
        Args:
            file_path: 文件路径
            file_name: 文件名
            format_type: 文件格式（html, markdown, pdf, mhtml）
        """
        if not os.path.exists(file_path):
            return
            
        download_url = os.path.join(file_path, file_name)
        logger.info("添加文件到文件列表：" + download_url)
        # 获取文件信息
        file_size = os.path.getsize(download_url)
        
        # 清理标题，移除平台名和日期信息
        logger.info("添加文件到文件列表：" + file_name)
        title = file_name.split('.')[0]
        logger.info("添加文件到文件列表：" + title)
        
        # 添加到文件列表
        self.file_list.append({
            "title": title,
            "download_url": download_url,
            "size": file_size,
            "format": format_type.replace('markdown', 'md')
        })

    def _extract_element(self, soup, selectors, default='', get_text=True):
        """提取页面元素
        Args:
            soup: BeautifulSoup对象
            selectors: 选择器列表，每个选择器是(tag, attrs)元组
            default: 默认返回值
            get_text: 是否只返回文本内容
        Returns:
            str or element: 提取的内容
        """
        
        for selector in selectors:
            try:
                tag, attrs = selector
                logger.debug(f"尝试选择器: tag={tag}, attrs={attrs}")
                
                # 处理正则表达式匹配
                regex_attrs = {}
                for key, value in attrs.items():
                    # 如果值是字符串且包含正则特殊字符，将其转换为正则对象
                    if isinstance(value, str) and any(c in value for c in '*?^$[](){}|'):
                        regex_attrs[key] = re.compile(value)
                    else:
                        regex_attrs[key] = value
                
                # 1. 首先尝试使用正则表达式匹配
                if regex_attrs:
                    element = soup.find(tag, regex_attrs)
                else:
                    element = soup.find(tag, attrs)

                # 2. 如果没找到且存在class_属性，尝试部分匹配
                if not element and 'class_' in attrs:
                    class_value = attrs['class_']
                    if isinstance(class_value, str):
                        # 支持正则表达式class匹配
                        if any(c in class_value for c in '*?^$[](){}|'):
                            elements = soup.find_all(tag, class_=re.compile(class_value))
                        else:
                            elements = soup.find_all(tag, class_=lambda x: x and class_value in x)
                        
                        if elements:
                            logger.info(f"通过class部分匹配找到元素: {class_value}")
                            element = elements[0]
                
                if element:
                    if get_text:
                        return element.get_text(strip=True)
                    return element
                    
            except Exception as e:
                logger.warning(f"选择器 {selector} 提取失败: {str(e)}")
                continue
                
        return default

    def _extract_title(self, soup):
        """提取文章标题
        Args:
            soup: BeautifulSoup对象
        Returns:
            str: 文章标题
        """
        return self._extract_element(soup, self.selectors['title'], 'UnknownTitle')

    def _extract_author(self, soup):
        """提取作者信息
        Args:
            soup: BeautifulSoup对象
        Returns:
            str: 作者名
        """
        return self._extract_element(soup, self.selectors['author'], 'UnknownAuthor')

    def _extract_content(self, soup):
        """提取文章内容
        Args:
            soup: BeautifulSoup对象
        Returns:
            Element: 文章内容元素
        """
        return self._extract_element(soup, self.selectors['content'], None, get_text=False)

    def _extract_date(self, soup):
        """提取文章发布日期
        Args:
            soup: BeautifulSoup对象
        Returns:
            str: 文章发布日期，格式为 YYYY-MM-DD
        """
        date = datetime.now().strftime('%Y-%m-%d')
        date_element = self._extract_element(soup, self.selectors['date'])
        logger.info("原始日期文本：" + str(date_element))
        if date_element:
            date = self._format_date(date_element)
            if isinstance(date, datetime):
                date = date.strftime('%Y-%m-%d')
        return str(date)

    def _format_date(self, date):
        """格式化日期为字符串
        Args:
            date: datetime对象或字符串
        Returns:
            str: 格式化的日期字符串 (YYYY-MM-DD)
        """
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, '%Y-%m-%d %H:%M')
            except ValueError:
                try:
                    date = datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    return datetime.now().strftime('%Y-%m-%d')
        
        return date.strftime('%Y-%m-%d')
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名中的非法字符
        Args:
            filename: 原始文件名
        Returns:
            str: 清理后的文件名
        """
        # 移除Windows文件名中的非法字符
        invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
        safe_name = re.sub(invalid_chars, '-', filename)
        # 去除所有空格
        safe_name = re.sub(r'[\s\u3000]+', '', safe_name)
        # 确保文件名不超过Windows限制（255字符）
        if len(safe_name) > 240:  # 留一些空间给扩展名
            safe_name = safe_name[:240]
        return safe_name
    
    
    def _get_file_name(self, format_type: str, prefix: str = None) -> str:
        """生成文件名
        Args:
            format_type: 文件格式，如 'html', 'pdf', 'markdown', 'mhtml'
            prefix: 可选的编号前缀，如 '001'
        Returns:
            str: 格式化的文件名
        """
        # 清理文件名中的非法字符
        safe_title = self._sanitize_filename(self.title)
        safe_author = self._sanitize_filename(self.author)
        # 获取文件扩展名
        format_extensions = {
            'html': '.html',
            'pdf': '.pdf',
            'markdown': '.md',
            'mhtml': '.mhtml'
        }
        extension = format_extensions.get(format_type, '')
        formatted_time = self.time if isinstance(self.time, str) else str(self.time)
        file_name = f"{safe_title}-{safe_author}-{self.platform_name}-{formatted_time}{extension}"
        logger.info("保存文件名：" + file_name)
        return file_name
    
    def _get_file_path(self, output_dir: str = None) -> str:
        """获取保存路径
        Args:
            output_dir: 输出目录
        Returns:
            str: 保存路径
        """
        # 使用平台名和时间创建目录
        base_dir = "blog"
        if output_dir:
            base_dir = output_dir
            
        # 创建目录
        os.makedirs(base_dir, exist_ok=True)

        # 创建作者文件夹
        folder_name = f"{self.platform_name}-{self._sanitize_filename(self.author)}"
        folder_path = os.path.join(base_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        logger.info("保存文件夹：" + folder_path)
        # 生成文件名
        return folder_path

    def _read_css_file(self, filename):
        """读取CSS文件内容"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading CSS file {filename}: {e}")
            return ""

    def _get_platform_css(self):
        """根据平台名称返回对应的CSS样式"""
        # CSS文件路径 - 修改为项目根目录下的css文件夹
        project_root = os.path.dirname(os.path.dirname(__file__))
        css_dir = os.path.join(project_root, 'css')
        base_css_path = os.path.join(css_dir, 'base.css')
        
        # 读取基础CSS
        css_content = self._read_css_file(base_css_path)
        
        # 如果指定了平台，添加平台特定的CSS
        platform_css_path = os.path.join(css_dir, f'{self.platform_flag}.css')
        if os.path.exists(platform_css_path):
            platform_css = self._read_css_file(platform_css_path)
            css_content += f"\n/* Platform specific styles for {self.platform_name} */\n{platform_css}"
        
        return css_content

    def _get_html_css(self, soup, base_url):
        """获取CSS样式
        Args:
            soup: BeautifulSoup对象
            base_url: 基本URL
        Returns:
            str: CSS样式字符串
        """
        # 处理微信特殊标签
        for element in soup.find_all(['div', 'section']):
            # 移除隐藏属性
            if 'style' in element.attrs:
                style = element['style']
                style = re.sub(r'visibility:\s*hidden', 'visibility: visible', style)
                style = re.sub(r'opacity:\s*0', 'opacity: 1', style)
                element['style'] = style
            
            # 移除微信特殊属性
            for attr in ['data-mpa-powered-by', 'data-tools', 'data-w-e', 'powered-by']:
                if attr in element.attrs:
                    del element[attr]
        
        # 从style标签中提取CSS
        css_styles = ""
        for style in soup.find_all('style'):
            if style.string:
                # 移除可能导致内容隐藏的样式
                style_text = style.string
                style_text = re.sub(r'visibility:\s*hidden', 'visibility: visible', style_text)
                style_text = re.sub(r'opacity:\s*0', 'opacity: 1', style_text)
                css_styles += style_text + '\n'
        
        # 从link标签中提取CSS
        for link in soup.find_all('link', rel='stylesheet'):
            if 'href' in link.attrs:
                css_url = urljoin(base_url, link['href'])
                try:
                    css_response = requests.get(css_url)
                    css_response.raise_for_status()
                    css_styles += css_response.text + '\n'
                except:
                    pass

        return css_styles

    def _fetch_css_styles(self, soup, base_url):
        """获取CSS样式
        Args:
            soup: BeautifulSoup对象
            base_url: 基本URL
        Returns:
            str: CSS样式字符串
        """
        css_styles = self._get_html_css(soup, base_url) + self._get_platform_css()     
        return css_styles
    
    def parse_blog(self, url: str, output_dir: str = None, save_options: dict = None) -> bool:
        """解析文章
        Args:
            url: 文章URL
            output_dir: 输出目录
            save_options: 保存选项
        Returns:
            bool: 是否成功
        """
        try:
            # 1. 获取页面内容
            html = self.fetch_html(url)
            #logger.info("页面内容" + html[2000:])
            if not html:
                return False
                
            # 2. 解析页面内容
            soup = BeautifulSoup(html, 'html.parser')
            self.author = self._extract_author(soup)
            self.time = self._extract_date(soup)
            self.title = self._extract_title(soup)
            self.content = self._extract_content(soup)

            logger.debug("内容：" + str(self.content) if self.content else "")
            logger.info("作者：" + str(self.author))
            logger.info("时间：" + str(self.time))
            logger.info("标题：" + str(self.title))

            
            if not all([self.title, self.content]):
                logger.error("解析文章失败：标题或内容为空")
                return False
            
            # 3. 获取保存路径
            file_path = self._get_file_path(output_dir)

            # 4. 保存文章
            self._css_styles = self._fetch_css_styles(soup, url)

            # 5. 返回结果
            success = self.save_blog(url, file_path, save_options)
            return success
            
        except Exception as e:
            logger.error(f"解析文章失败: {str(e)}")
            return False
        
    def fetch_html(self, url: str) -> str:
        """获取页面HTML内容
        Args:
            url: 页面URL
        Returns:
            str: HTML内容
        """
        try:
            response = self._session.get(url, headers=self._headers, timeout=30)
            response.raise_for_status()
            self.base_html = response.text
            return self.base_html
        except Exception as e:
            logger.error(f"获取页面失败: {str(e)}")
            return None
        

    def save_blog(self, url: str, file_path: str, save_options: dict = None):
        logger.info("开始保存文章")
        if not save_options:
            save_options = {'html': True}
            
        success = False
        for format_type, enabled in save_options.items():
            if enabled and format_type in self.save_handlers:
                handler = self.save_handlers[format_type]
                file_name = self._get_file_name(format_type)
                result = handler(
                    title=self.title,
                    content=self.content,
                    css_styles=self._css_styles,
                    file_name=file_name,
                    file_path=file_path,
                    base_url=url,
                    platform=self.platform_flag
                )
                success = success or bool(result)
                if result:
                    self._add_file_to_list(file_path, file_name, format_type)

        return success