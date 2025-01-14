#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, HttpUrl, field_validator, validator
from typing import List
from pathlib import Path
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from dotenv import load_dotenv
import zipfile
import io
from core.blog_parser import BlogParser
from fastapi.responses import FileResponse as FastAPIFileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from core.log_utils import logger
from datetime import datetime
from urllib.parse import quote
import os
import shutil
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import time

# 加载环境变量
load_dotenv()

# 获取配置
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '3102'))

# 从环境变量获取 CORS 配置
# CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
# logger.info(f"从环境变量读取的 CORS_ORIGINS: {CORS_ORIGINS}")
# # 过滤掉空字符串
# CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS if origin.strip()]
# logger.info(f"最终的 CORS_ORIGINS: {CORS_ORIGINS}")

# 创建FastAPI应用
app = FastAPI(title="BlogKeeper API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 使用配置的源
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 明确指定允许的方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["Content-Disposition"],  # 暴露文件下载所需的头部
)

# 创建临时文件目录
TEMP_PATH = "temp"
TEMP_DIR = Path(TEMP_PATH)
TEMP_DIR.mkdir(exist_ok=True)

DOWNLOAD_DIR = "/download"

# 挂载临时文件目录
app.mount(DOWNLOAD_DIR, StaticFiles(directory=str(TEMP_DIR)), name="download")

class ParseRequest(BaseModel):
    url: HttpUrl
    fileContent: bool
    formats: List[str]
    
    @field_validator('formats')
    def validate_formats(cls, v):
        valid_formats = {'html', 'md', 'pdf', 'mhtml'}
        for fmt in v:
            if fmt not in valid_formats:
                raise ValueError(f'Invalid format: {fmt}. Valid formats are: {valid_formats}')
        return v

class FileInfo(BaseModel):
    title: str
    download_url: str
    size: int
    format: str
    file_content: str

class BatchDownloadFile(BaseModel):
    url: str
    filename: str

    @field_validator('url')
    def validate_url(cls, v):
        if not v.startswith('/download/'):
            raise ValueError('URL must start with /download/')
        return v

class BatchDownloadRequest(BaseModel):
    files: List[BatchDownloadFile]

    @field_validator('files')
    def validate_files(cls, v):
        if not v:
            raise ValueError('files list cannot be empty')
        return v

@app.post("/batch-download")
async def batch_download(request: Request, body: BatchDownloadRequest):
    start_time = time.time()
    try:
        raw_body = await request.body()
        logger.info(f"原始请求体: {raw_body}")
        logger.info(f"解析后的请求参数: {body.dict()}")

        # 创建内存中的ZIP文件
        zip_buffer = io.BytesIO()
        # 获取第一个文件名作为zip文件名
        first_file = body.files[0] if body.files else None
        filename_without_ext = first_file.filename.rsplit('.', 1)[0] if first_file else "blog_content"
        zip_filename = f"{filename_without_ext}.zip"

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_info in body.files:
                # 获取完整的文件路径
                file_path = TEMP_PATH + file_info.url[len(DOWNLOAD_DIR):]
                logger.info(f"处理文件: URL={file_info.url}, 路径={file_path}, 文件名={file_info.filename}")

                # 获取完整的文件路径
                full_path = Path(file_path)
                logger.info(f"完整路径: {full_path}")

                # 检查文件是否存在
                if not full_path.is_file():
                    raise HTTPException(
                        status_code=404,
                        detail=f"文件不存在: {file_info.filename}"
                    )

                # 将文件添加到ZIP，使用传入的文件名
                zip_file.write(full_path, file_info.filename)
                logger.info(f"已添加到ZIP: {file_info.filename}")

        # 将ZIP文件指针移到开头
        zip_buffer.seek(0)

        logger.info(f"生成ZIP文件: {zip_filename}")

        # 记录处理时间
        total_time = time.time() - start_time
        logger.info("=== 批量下载性能统计 ===")
        logger.info(f"总处理时间: {total_time:.2f}秒")

        # 返回ZIP文件，使用 urllib.parse.quote 处理中文文件名
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename*=UTF-8\'\'{quote(zip_filename)}'
            }
        )

    except ValueError as e:
        logger.error(f"请求参数验证失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"批量下载失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/parse", response_model=List[FileInfo])
async def parse_blog_api(request: ParseRequest):
    start_time = time.time()
    try:
        # 创建输出目录
        output_dir = TEMP_DIR / str(hash(str(request.url)))
        output_dir.mkdir(exist_ok=True)

        # 格式映射
        format_mapping = {
            'md': 'markdown',
            'html': 'html',
            'pdf': 'pdf',
            'mhtml': 'mhtml'
        }

        # 转换格式名称
        formats = [format_mapping.get(fmt, fmt) for fmt in request.formats]
        logger.info(f"请求的原始格式: {request.formats}")
        logger.info(f"转换后的格式: {formats}")

        # 是否返回文件内容
        file_content = request.fileContent

        # 准备保存选项
        save_options = {
            'formats': formats
        }

        # 创建解析器并解析博客
        parser = BlogParser()
        parse_start = time.time()
        success = parser.parse(str(request.url), str(output_dir), save_options)
        parse_time = time.time() - parse_start

        if not success:
            raise HTTPException(status_code=500, detail="博客解析失败")

        # 获取文件列表
        files = []
        file_list = parser.get_file_list()
        #logger.info(f"原始文件列表: {file_list}")

        # 只返回请求的格式
        for file_info in file_list:
            if file_info['format'] in formats:
                # 修改下载URL的格式，确保使用正斜杠
                file_path = file_info["download_url"]
                file_path = file_path.replace('\\', '/')
                file_path = file_path.replace(TEMP_PATH, DOWNLOAD_DIR)
                file_info['download_url'] = file_path

                if not file_content:
                    file_info['file_content'] = ""

                logger.info(f"处理后的文件信息: {file_info}")
                files.append(FileInfo(**file_info))

        # 记录处理时间
        total_time = time.time() - start_time
        logger.info("\n=== 博客解析性能统计 ===")
        logger.info(f"总处理时间: {total_time:.2f}秒")
        logger.info(f"内容解析时间: {parse_time:.2f}秒")

        logger.info(f"最终返回的文件列表: {files}")
        if not files:
            raise HTTPException(status_code=500, detail="未生成任何文件")
            
        return files

    except Exception as e:
        logger.error(f"解析博客时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 定义清理函数
def cleanup_directories():
    try:
        # 获取当前时间
        now = datetime.now()
        print(f"开始清理目录... {now}")

        # 清理temp目录
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            print(f"已清理temp目录: {temp_dir}")

        # 清理blog目录
        blog_dir = os.path.join(os.path.dirname(__file__), 'blog')
        if os.path.exists(blog_dir):
            shutil.rmtree(blog_dir)
            os.makedirs(blog_dir)
            print(f"已清理blog目录: {blog_dir}")

    except Exception as e:
        print(f"清理目录时出错: {str(e)}")

# 创建调度器
scheduler = BackgroundScheduler()
# 添加定时任务，每天凌晨12:00执行
scheduler.add_job(cleanup_directories, 'cron', hour=0, minute=0)
# 添加测试用的定时任务，每分钟执行一次（仅在测试时启用）
# scheduler.add_job(cleanup_directories, 'interval', minutes=1)
# 启动调度器
scheduler.start()

# 启动服务器
if __name__ == "__main__":
    logger.info(f"正在启动服务器，HOST={API_HOST}, PORT={API_PORT}")
    try:
        import uvicorn
        uvicorn.run(
            app,
            host=API_HOST,
            port=API_PORT,
            reload=False  # 关闭reload模式，避免platform相关问题
        )
    except Exception as e:
        logger.error(f"启动服务器失败: {str(e)}")
        raise
