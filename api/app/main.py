#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.blog_parser import BlogParser
from core.arg_utils import ArgUtils
from core.log_utils import logger

def main():
    try:
        # 显示启动标志
        ArgUtils.print_banner()
        
        # 初始化参数工具类
        args = ArgUtils()
        args.parse_args()
        
        # 获取URL
        url = args.get_url()
        if not url:
            logger.error("请提供博客文章的URL")
            return
        
        logger.info(f"开始处理博客文章: {url}")
        
        # 使用全局便捷函数解析文章
        parser = BlogParser()
        success = parser.parse(url, args.get_output_dir(), args.get_save_options())
        
        if success:
            logger.info("文章处理完成")
        else:
            logger.error("文章处理失败")
                
    except Exception as e:
        logger.critical(f"程序执行出错: {str(e)}", exc_info=True)
        return

if __name__ == "__main__":
    main()