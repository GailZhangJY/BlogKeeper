import os
import yaml
import random
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        """初始化配置管理器
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件
        Returns:
            Dict: 配置字典
        """
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"配置文件不存在: {self.config_path}")
                return {}
                
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.debug(f"成功加载配置文件: {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}
            
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """获取指定平台的配置
        Args:
            platform: 平台名称
        Returns:
            Dict: 平台配置
        """
        return self.config.get(platform, {})
        
    def get_common_config(self) -> Dict[str, Any]:
        """获取通用配置
        Returns:
            Dict: 通用配置
        """
        return self.config.get('common', {})
        
    def get_random_user_agent(self) -> str:
        """获取随机 User-Agent
        Returns:
            str: User-Agent 字符串
        """
        user_agents = self.get_common_config().get('user_agents', [])
        return random.choice(user_agents) if user_agents else ""
        
    def get_cookies(self, platform: str) -> Dict[str, str]:
        """获取指定平台的 cookies
        Args:
            platform: 平台名称
        Returns:
            Dict: cookie 字典
        """
        platform_config = self.get_platform_config(platform)
        return platform_config.get('cookies', {})
        
    def get_headers(self, platform: str) -> Dict[str, str]:
        """获取指定平台的请求头
        Args:
            platform: 平台名称
        Returns:
            Dict: 请求头字典
        """
        platform_config = self.get_platform_config(platform)
        headers = platform_config.get('headers', {}).copy()
        
        # 添加通用请求头
        headers.update({
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        
        return headers
        
    def get_endpoint(self, platform: str, endpoint_name: str, **kwargs) -> Optional[str]:
        """获取指定平台的 API 端点
        Args:
            platform: 平台名称
            endpoint_name: 端点名称
            **kwargs: 格式化参数
        Returns:
            str: 格式化后的 URL
        """
        platform_config = self.get_platform_config(platform)
        endpoints = platform_config.get('endpoints', {})
        endpoint = endpoints.get(endpoint_name)
        
        if endpoint:
            try:
                return endpoint.format(**kwargs)
            except KeyError as e:
                logger.error(f"格式化端点 URL 失败，缺少参数: {str(e)}")
                return None
        return None
        
    def get_retry_config(self) -> tuple:
        """获取重试配置
        Returns:
            tuple: (重试次数, 重试延迟)
        """
        common_config = self.get_common_config()
        return (
            common_config.get('retry_times', 3),
            common_config.get('retry_delay', 1)
        )
        
    def get_timeout(self) -> int:
        """获取超时设置
        Returns:
            int: 超时秒数
        """
        return self.get_common_config().get('timeout', 30)
