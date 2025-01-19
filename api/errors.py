from typing import Optional, Dict, Any
from fastapi import HTTPException

class BlogKeeperError(Exception):
    """基础错误类"""
    def __init__(
        self,
        message: str,
        error_type: str,
        status_code: int = 500,
        suggestion: Optional[str] = None,
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.suggestion = suggestion
        super().__init__(message)

    def to_dict(self) -> dict:
        """转换为字典格式，用于API响应"""
        return {
            "code": self.status_code,
            "type": self.error_type,
            "message": self.message,
            "suggestion": self.suggestion
        }

    def to_http_exception(self) -> HTTPException:
        """转换为FastAPI的HTTPException"""
        return HTTPException(
            status_code=self.status_code,
            detail=self.to_dict()
        )

class NetworkError(BlogKeeperError):
    """网络相关错误"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_type="NetworkError",
            status_code=503,
            suggestion="请检查网络连接或稍后重试"
        )

class ParseError(BlogKeeperError):
    """解析相关错误"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_type="ParseError",
            status_code=422,
            suggestion="解析失败，请稍后重试"
        )

class AuthError(BlogKeeperError):
    """认证相关错误"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_type="AuthError",
            status_code=401,
            suggestion="请检查链接是否需要登录或访问权限"
        )

class PlatformError(BlogKeeperError):
    """不支持的平台错误"""
    def __init__(self, domain: str, supported_platforms: list = None):
        platforms_str = "、".join(supported_platforms) if supported_platforms else "CSDN、博客园、微信公众号"
        super().__init__(
            message=f"不支持的博客平台: {domain}",
            error_type="PlatformError",
            status_code=400,
            suggestion=f""
        )

class FormatError(BlogKeeperError):
    """格式转换错误"""
    def __init__(self, message: str, supported_formats: list = None):
        formats_str = "、".join(supported_formats) if supported_formats else "HTML、Markdown、PDF、MHTML"
        super().__init__(
            message=message,
            error_type="FormatError",
            status_code=422,
            suggestion=f"目前支持以下格式：{formats_str}"
        )

class ServerError(BlogKeeperError):
    """服务器内部错误"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_type="ServerError",
            status_code=500,
            suggestion="请稍后重试或联系管理员"
        )
