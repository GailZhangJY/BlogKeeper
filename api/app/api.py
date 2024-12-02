#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, HttpUrl, validator
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

# 加载环境变量
load_dotenv()

# 获取配置
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '3102'))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

# 创建FastAPI应用
app = FastAPI(title="BlogKeeper API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，生产环境建议设置具体的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
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
    formats: List[str]

class FileInfo(BaseModel):
    title: str
    download_url: str
    size: int
    format: str

class BatchDownloadFile(BaseModel):
    url: str
    filename: str

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith('/download/'):
            raise ValueError('URL must start with /download/')
        return v

class BatchDownloadRequest(BaseModel):
    files: List[BatchDownloadFile]

    @validator('files')
    def validate_files(cls, v):
        if not v:
            raise ValueError('files list cannot be empty')
        return v

@app.post("/batch-download")
async def batch_download(request: Request, body: BatchDownloadRequest):
    """批量下载文件并打包成ZIP"""
    try:
        raw_body = await request.body()
        logger.info(f"原始请求体: {raw_body}")
        logger.info(f"解析后的请求参数: {body.dict()}")
        
        # 创建内存中的ZIP文件
        zip_buffer = io.BytesIO()
        # 获取第一个文件名作为zip文件名
        first_file = body.files[0] if body.files else None
        zip_filename = first_file.filename if first_file else "blog_content.zip"
        # 确保zip_filename有.zip扩展名
        if not zip_filename.endswith('.zip'):
            zip_filename += '.zip'
        
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
    try:
        # 创建输出目录
        output_dir = TEMP_DIR / str(hash(str(request.url)))
        output_dir.mkdir(exist_ok=True)
        
        # 准备保存选项
        save_options = {
            "html": "html" in request.formats,
            "markdown": "md" in request.formats,
            "pdf": "pdf" in request.formats,
            "mhtml": "mhtml" in request.formats
        }
        
        # 创建解析器并解析博客
        parser = BlogParser()
        success = parser.parse(str(request.url), str(output_dir), save_options)
        
        if not success:
            raise HTTPException(status_code=500, detail="博客解析失败")
        
        # 获取文件列表
        files = []
        file_list = parser.get_file_list()
        logger.info(f"原始文件列表: {file_list}")
        
        # 格式映射
        format_mapping = {
            "markdown": "md",
            "html": "html",
            "pdf": "pdf",
            "mhtml": "mhtml"
        }
        
        requested_formats = set(format_mapping.get(fmt, fmt) for fmt in request.formats)
        logger.info(f"请求的格式: {requested_formats}")
        
        for file_info in file_list:
            file_path = file_info["download_url"]
            file_path = file_path.replace('\\', '/')
            file_path = file_path.replace(TEMP_PATH, DOWNLOAD_DIR)
            file_info["download_url"] = file_path

            logger.info(f"处理后的文件信息: {file_info}")
            files.append(FileInfo(**file_info))

        
        logger.info(f"最终返回的文件列表: {files}")
        return files
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
