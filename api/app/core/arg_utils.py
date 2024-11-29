import argparse
from typing import List, Dict, Optional
from colorama import init, Fore, Style
import random

class ArgUtils:
    """参数处理工具类"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ArgUtils, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.parser = argparse.ArgumentParser(description='博客文章下载工具')
        self._setup_arguments()
        self.args = None
    
    @staticmethod
    def print_banner():
        """打印启动标志"""
        banner = r"""
 ____  _                  _             _     _            
| __ )| | ___   __ _    / \   _ __ ___| |__ (_)_   _____ 
|  _ \| |/ _ \ / _` |  / _ \ | '__/ __| '_ \| \ \ / / _ \
| |_) | | (_) | (_| | / ___ \| | | (__| | | | |\ V /  __/
|____/|_|\___/ \__, |/_/   \_\_|  \___|_| |_|_| \_/ \___|
               |___/                                       

        [ BlogArchive v1.0 - Your Blog Content Keeper ]
        [ Author: Python Developer               ]
        [ https://github.com/your-repo           ]
        """
        # 使用不同的颜色让标志更炫酷
        try:
            init()
            
            # 可用的颜色列表
            colors = [Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.RED, Fore.GREEN, Fore.BLUE]
            
            lines = banner.split('\n')
            # ASCII art部分使用随机颜色
            art_color = random.choice(colors)
            for i in range(1, 7):
                print(f"{art_color}{lines[i]}{Style.RESET_ALL}")
            
            # 信息部分使用不同的颜色
            for i in range(7, len(lines)):
                if lines[i].strip():
                    print(f"{random.choice(colors)}{lines[i]}{Style.RESET_ALL}")
                else:
                    print(lines[i])
                    
        except ImportError:
            # 如果没有colorama，就使用普通输出
            print(banner)
    
    def _setup_arguments(self):
        """设置命令行参数"""
        self.parser.add_argument('url', help='博客文章的URL')
        
        # 保存选项
        self.parser.add_argument('-html', action='store_true', help='保存为HTML格式')
        self.parser.add_argument('-pdf', action='store_true', help='保存为PDF格式')
        self.parser.add_argument('-md', '--markdown', action='store_true', help='保存为Markdown格式')
        self.parser.add_argument('-mhtml', action='store_true', help='保存为MHTML格式')
        
        # 输出目录
        self.parser.add_argument('-o', '--output', help='指定输出目录')
        
    def parse_args(self):
        """解析命令行参数"""
        self.args = self.parser.parse_args()
        
        # 如果没有指定任何保存格式，默认使用HTML
        if not any([self.args.html, self.args.pdf, self.args.markdown, self.args.mhtml]):
            self.args.html = True
    
    def get_url(self) -> str:
        """获取URL"""
        return self.args.url if self.args else None
    
    def get_save_options(self) -> Dict[str, bool]:
        """获取保存选项"""
        if not self.args:
            return {'html': True}
            
        return {
            'html': self.args.html,
            'pdf': self.args.pdf,
            'markdown': self.args.markdown,
            'mhtml': self.args.mhtml
        }
    
    def get_output_dir(self) -> Optional[str]:
        """获取输出目录"""
        return self.args.output if self.args else None
