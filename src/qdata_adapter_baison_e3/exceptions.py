"""
baison-e3 适配器异常定义
"""

from qdata_adapter.exceptions import AdapterError, AuthenticationError, ResponseError


class BaisonE3AdapterError(AdapterError):
    """
    baison-e3 适配器基础异常

    Example:
        >>> raise BaisonE3AdapterError("操作失败", code="OP_FAILED")
    """

    def __init__(self, message: str, code: str = "BAISON_E3_ERROR", details: dict | None = None):
        super().__init__(message, code, details)


class BaisonE3AdapterAuthError(AuthenticationError):
    """
    baison-e3 认证失败异常

    Example:
        >>> raise BaisonE3AdapterAuthError("Invalid API key")
    """

    def __init__(self, message: str = "Authentication failed", details: dict | None = None):
        super().__init__(message, "BAISON_E3_AUTH_ERROR", details)


class BaisonE3AdapterAPIError(ResponseError):
    """
    baison-e3 API 错误异常

    Attributes:
        status_code: HTTP 状态码
        api_code: baison-e3 错误码

    Example:
        >>> raise BaisonE3AdapterAPIError(
        ...     "API call failed",
        ...     status_code=500,
        ...     api_code="INTERNAL_ERROR"
        ... )
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        api_code: str | None = None,
        response_body: dict | None = None,
        details: dict | None = None,
    ):
        details = details or {}
        if api_code is not None:
            details["api_code"] = api_code
        super().__init__(message, "BAISON_E3_API_ERROR", status_code, response_body, details)
        self.api_code = api_code


__all__ = [
    "BaisonE3AdapterError",
    "BaisonE3AdapterAuthError",
    "BaisonE3AdapterAPIError",
]