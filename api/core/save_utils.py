#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import markdownify
import base64
import requests
import shutil
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import time
import zipfile
import sys
import tempfile
import platform
import html2text
import pdfkit
import random
import string
import quopri
import uuid
import io
from PIL import Image
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from .log_utils import logger

def get_save_path(file_name, file_path):
    # 拼接文件路径
    filepath = os.path.join(file_path, file_name)
    # 确保文件夹存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    return filepath


def base_save_handle(title, content, css_styles, file_name, file_path, base_url=None, platform=None):
    # 处理图片
    logger.info("base_save_handle 处理图片" + base_url)
    logger.info(f"content类型: {type(content)}")
    if base_url:
        logger.info("base_save_handle 处理图片00" + base_url)
        content = process_images_in_content(content, base_url, file_path)
        
    # 如果content是BeautifulSoup对象，转换为字符串
    if isinstance(content, BeautifulSoup):
        content = str(content)

    return content

def create_html_template(title, content, css_styles, base_url=None, platform=None):
    # 创建HTML模板
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            {css_styles}
        </style>
    </head>
    <body>
        <article>
            <h1><a href={base_url}>{title}</a></h1>
            {content}
        </article>
    </body>
    </html>
    """
    return html_template
    
def save_as_html(title, content, css_styles, file_name, file_path, base_url=None, platform=None):
    """将博客内容保存为HTML格式
    Args:
        title: 文章标题
        content: 文章内容
        css_styles: CSS样式内容
        file_name: 文件名
        file_path: 保存的文件夹路径
        base_url: 原始页面的URL，用于处理相对路径
        platform: 平台名称，用于加载特定的CSS样式
    Returns:
        str: 保存的文件路径
    """
    try:
        filepath = get_save_path(file_name, file_path)
        content = base_save_handle(title, content, css_styles, file_name, file_path, base_url, platform)
            
        # 创建HTML模板
        html_template = create_html_template(title, content, css_styles, base_url, platform)
        
        # 保存HTML文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_template)
            
        logger.info(f"HTML文件已保存: {filepath}")
        return { 'file_path': filepath, 'file_content': html_template}
        
    except Exception as e:
        logger.error(f"保存HTML文件时出错: {str(e)}")
        return None

def save_as_markdown(title, content, css_styles, file_name, file_path, base_url=None, platform=None):
    """将博客内容保存为Markdown格式
    Args:
        title: 文章标题
        content: 文章内容
        css_styles: CSS样式内容
        file_name: 文件名
        file_path: 保存的文件夹路径
        base_url: 原始页面的URL，用于处理相对路径
        platform: 平台名称，用于加载特定的CSS样式
    Returns:
        str: 保存的文件路径
    """
    try:
        filepath = get_save_path(file_name, file_path)
        content = base_save_handle(title, content, css_styles, file_name, file_path, base_url, platform)
            
        # 将HTML转换为Markdown
        markdown_converter = html2text.HTML2Text()
        markdown_converter.body_width = 0  # 不限制行宽
        markdown_content = markdown_converter.handle(content)
        
        # 添加标题
        final_content = f"# {title}\n\n{markdown_content}"
        
        # 保存Markdown文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
            
        logger.info(f"Markdown文件已保存: {filepath}")
        return  { 'file_path': filepath, 'file_content': final_content}
        
    except Exception as e:
        logger.error(f"保存Markdown文件时出错: {str(e)}")
        return None

def get_wkhtmltopdf_path() -> str:
    """
    获取 wkhtmltopdf 可执行文件的路径
    Linux 使用系统安装的版本，Windows 使用项目自带的版本
    """
    if platform.system() == 'Windows':
        # Windows 使用项目自带的版本
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        wkhtmltopdf_path = os.path.join(base_dir, 'tools', 'wkhtmltopdf', 'bin', 'wkhtmltopdf.exe')
        if not os.path.exists(wkhtmltopdf_path):
            raise FileNotFoundError(f'wkhtmltopdf not found at {wkhtmltopdf_path}')
        return wkhtmltopdf_path
    else:
        # Linux 使用系统安装的版本
        # 尝试多个可能的路径
        possible_paths = [
            '/usr/local/bin/wkhtmltopdf',
            '/usr/bin/wkhtmltopdf',
            'wkhtmltopdf'  # 如果在 PATH 中
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
            # 对于 'wkhtmltopdf'，使用 which 命令检查
            elif path == 'wkhtmltopdf':
                try:
                    import subprocess
                    result = subprocess.run(['which', 'wkhtmltopdf'], capture_output=True, text=True)
                    if result.returncode == 0:
                        return 'wkhtmltopdf'
                except:
                    pass
        raise FileNotFoundError('wkhtmltopdf not found in system')

def save_as_pdf(title, content, css_styles, file_name, file_path, base_url=None, platform=None):
    """将博客内容保存为PDF格式"""
    try:
        # 1. 处理图片
        content = base_save_handle(title, content, css_styles, file_name, file_path, base_url, platform)
        
        # 2. 先保存为临时HTML文件
        temp_html = os.path.join(file_path, f"{os.path.splitext(file_name)[0]}_temp.html")
        with open(temp_html, 'w', encoding='utf-8') as f:
            html_content = create_html_template(title, content, css_styles, base_url, platform)
            f.write(html_content)
        
        # 3. 配置wkhtmltopdf选项
        options = {
            'enable-local-file-access': None,  # 允许访问本地文件
            'encoding': 'utf-8',
            'javascript-delay': '1000',  # 等待JavaScript执行
            'no-stop-slow-scripts': None,  # 不要停止慢脚本
            'enable-javascript': None,  # 启用JavaScript
        }
        
        # 4. 生成PDF文件路径
        pdf_path = os.path.join(file_path, file_name)
        
        try:
            # 5. 使用wkhtmltopdf转换
            config = pdfkit.configuration(wkhtmltopdf=get_wkhtmltopdf_path())
            pdfkit.from_file(temp_html, pdf_path, options=options, configuration=config)
            
            # 6. 删除临时HTML文件
            os.remove(temp_html)
            return { 'file_path': pdf_path, 'file_content': ""}
            
        except Exception as e:
            logger.error(f"PDF转换失败: {str(e)}")
            # 如果转换失败，尝试直接从HTML字符串转换
            try:
                pdfkit.from_string(html_content, pdf_path, options=options, configuration=config)
                return { 'file_path': pdf_path, 'file_content': ""}
            except Exception as e2:
                logger.error(f"从字符串转换PDF也失败: {str(e2)}")
                return None
                
    except Exception as e:
        logger.error(f"保存PDF文件时出错: {str(e)}")
        return None

def save_as_mhtml(title, content, css_styles, file_name, file_path, base_url=None, platform=None):
    """将HTML内容保存为MHTML格式
    Args:
        title: 文章标题
        content: 文章内容
        css_styles: CSS样式内容
        file_name: 文件名
        file_path: 保存的文件夹路径
        base_url: 原始页面的URL，用于处理相对路径
        platform: 平台名称，用于加载特定的CSS样式
    Returns:
        str: 保存的文件路径
    """
    try:
        # 编码HTML内容
        filepath = get_save_path(file_name, file_path)
        content = base_save_handle(title, content, css_styles, file_name, file_path, base_url, platform)
        html_content = create_html_template(title, content, css_styles, base_url, platform)

        # 处理图片
        images = handle_mhtml_images(content, base_url)

        # 生成MHTML头部
        boundary = '----=_NextPart_' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        mhtml_header = (
            f'From: <Saved by BlogTest>\n'
            f'Subject: {title}\n'
            f'Date: {datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")}\n'
            f'MIME-Version: 1.0\n'
            f'Content-Type: multipart/related;\n'
            f'\tboundary="{boundary}"\n\n'
        )

        # 保存MHTML文件
        with open(filepath, 'w', encoding='utf-8') as f:
            # 1. 写入MHTML头部
            f.write(mhtml_header)
            
            # 2. 写入HTML内容部分
            f.write(f'--{boundary}\n')
            f.write('Content-Type: text/html; charset="utf-8"\n')
            f.write('Content-Transfer-Encoding: quoted-printable\n')
            if base_url:
                f.write(f'Content-Location: {base_url}\n')
            f.write('\n')  # 空行很重要
            f.write(quopri.encodestring(html_content.encode('utf-8')).decode('utf-8'))
            
            # 3. 写入图片内容
            for img in images:
                f.write(f'\n--{boundary}\n')
                f.write(f'Content-Type: {img["content_type"]}\n')
                f.write('Content-Transfer-Encoding: base64\n')
                f.write(f'Content-Location: {img["src"]}\n')
                f.write('\n')  # 空行很重要
                f.write(img['data'])
            
            # 4. 写入结束标记
            f.write(f'\n--{boundary}--\n')
            
        logger.info(f"MHTML文件已保存: {filepath}")
        return  { 'file_path': filepath, 'file_content': ""}
        
    except Exception as e:
        logger.error(f"保存MHTML文件时出错: {str(e)}")
        return None

def handle_mhtml_images(content, base_url):
    # 处理图片并收集图片信息
    if isinstance(content, str):
        soup = BeautifulSoup(content, 'html.parser')
    else:
        soup = content
        
    images = []
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src:
            try:
                # 如果是相对路径，转换为绝对路径
                if not src.startswith(('http://', 'https://')):
                    src = urljoin(base_url, src)
                
                # 下载图片内容
                response = requests.get(src)
                if response.status_code == 200:
                    # 获取图片类型
                    content_type = response.headers.get('content-type', 'image/jpeg')
                    # 获取图片内容并进行base64编码
                    img_data = base64.b64encode(response.content).decode('utf-8')
                    images.append({
                        'src': src,
                        'content_type': content_type,
                        'data': img_data
                    })
                    logger.info(f"成功下载图片: {src}")
            except Exception as e:
                logger.error(f"下载图片失败 {src}: {str(e)}")
                continue
    return images

def convert_webp_to_png(image_url, save_dir):
    """将webp格式图片转换为png格式
    Args:
        image_url: 图片URL
        save_dir: 保存目录
    Returns:
        str: 转换后的图片路径，如果转换失败则返回原URL
    """
    try:
        logger.info(f"开始处理webp图片: {image_url}")
        
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        logger.info(f"图片将保存到: {save_dir}")
        
        # 下载图片
        logger.info("正在下载图片...")
        response = requests.get(image_url)
        if response.status_code != 200:
            logger.error(f"下载图片失败: {image_url}, 状态码: {response.status_code}")
            return image_url
            
        # 生成唯一的文件名
        filename = f"img_{uuid.uuid4().hex[:8]}.png"
        save_path = os.path.join(save_dir, filename)
        logger.info(f"生成的文件名: {filename}")
        logger.info(f"完整保存路径: {save_path}")
        
        # 转换图片格式
        try:
            logger.info("正在转换图片格式...")
            image = Image.open(io.BytesIO(response.content))
            logger.info(f"原始图片信息: 模式={image.mode}, 大小={image.size}")
            
            # 如果图片有透明通道，保留alpha通道
            if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
                logger.info("检测到透明通道，保留alpha通道")
                image = image.convert('RGBA')
            else:
                logger.info("转换为RGB模式")
                image = image.convert('RGB')
                
            image.save(save_path, 'PNG')
            logger.info(f"✅ 图片已成功转换并保存: {save_path}")
            relative_path = os.path.join('images', filename)
            logger.info(f"返回相对路径: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.error(f"转换图片失败: {str(e)}")
            logger.error("详细错误信息:")
            import traceback
            logger.error(traceback.format_exc())
            return image_url
            
    except Exception as e:
        logger.error(f"处理图片时发生错误: {str(e)}")
        logger.error("详细错误信息:")
        import traceback
        logger.error(traceback.format_exc())
        return image_url

def process_single_image(img, base_url, images_dir):
    """处理单个图片"""
    start_time = time.time()
    try:
        # 检查所有可能的图片源属性
        src_attrs = ['src', 'data-src', 'data-original-src', 'data-backgroud', 'data-original']
        src = None
        for attr in src_attrs:
            if attr in img.attrs and img[attr]:
                src = img[attr]
                break
                
        if not src:
            return False, None, None, 0
            
        # 处理双斜杠开头的URL
        if src.startswith('//'):
            src = 'https:' + src
            
        # 转换为绝对URL
        if not src.startswith(('http://', 'https://')):
            src = urljoin(base_url, src)
            
        # 检查是否为webp格式
        if '.webp' in src.lower() or 'format/webp' in src.lower():
            # 如果是简书的图片URL，尝试去掉format/webp参数
            if 'jianshu.io' in src and 'format/webp' in src:
                new_src = re.sub(r'\|imageView2/2/w/\d+/format/webp', '', src)
                new_src = re.sub(r'\?.*format/webp', '', new_src)
                return True, src, new_src, time.time() - start_time
                
            # 转换并保存图片
            new_src = convert_webp_to_png(src, images_dir)
            if new_src != src:
                return True, src, new_src, time.time() - start_time
                
        return True, src, src, time.time() - start_time
        
    except Exception as e:
        logger.error(f"处理图片失败: {str(e)}")
        return False, None, None, time.time() - start_time

def process_images_in_content(content, base_url, save_dir):
    """处理文章内容中的图片，使用并行处理提高性能"""
    start_time = time.time()
    logger.info("=== 开始并行处理文章中的图片 ===")
    
    if isinstance(content, str):
        soup = BeautifulSoup(content, 'html.parser')
    else:
        soup = content
        
    images = soup.find_all('img')
    if not images:
        return str(soup)
        
    images_dir = os.path.join(save_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    processing_times = []
    
    def process_image_wrapper(img):
        success, old_src, new_src, process_time = process_single_image(img, base_url, images_dir)
        logger.info(f"图片处理结果: {success}, 原始URL: {old_src}, 新URL: {new_src}, 处理时间: {process_time:.2f}秒")
        processing_times.append(process_time)
        if success and new_src:
            img['src'] = new_src
            # 移除其他可能的图片源属性
            for attr in ['data-src', 'data-original']:
                if attr in img.attrs:
                    del img[attr]
    
    # 使用线程池并行处理图片
    with ThreadPoolExecutor(max_workers=min(32, len(images))) as executor:
        list(executor.map(process_image_wrapper, images))
    
    total_time = time.time() - start_time
    if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
        max_time = max(processing_times)
        parallel_efficiency = sum(processing_times)/total_time if total_time > 0 else 0
    else:
        avg_time = 0
        max_time = 0
        parallel_efficiency = 0
    
    logger.info(f"=== 图片处理完成 ===")
    logger.info(f"总图片数: {len(images)}")
    logger.info(f"总处理时间: {total_time:.2f}秒")
    logger.info(f"平均处理时间: {avg_time:.2f}秒/图片")
    logger.info(f"最长处理时间: {max_time:.2f}秒")
    logger.info(f"并行处理效率提升: {parallel_efficiency:.1f}倍")
    
    return str(soup)

__all__ = [
    'save_as_html',
    'save_as_pdf',
    'save_as_markdown',
    'save_as_mhtml',
]