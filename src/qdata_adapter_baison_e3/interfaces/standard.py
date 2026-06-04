"""
baison-e3 standard 接口实现

主接口实现，基于平台的标准 API。
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, AsyncIterator

from qdata_adapter.exceptions import AuthenticationError, NotFoundError, ValidationError

from qdata_adapter_baison_e3.exceptions import BaisonE3AdapterAPIError, BaisonE3AdapterAuthError
from qdata_adapter_baison_e3.interfaces.base import BaseInterface

if TYPE_CHECKING:
    from qdata_adapter.client import HttpClient
    from qdata_adapter.context import ConnectorContext

logger = logging.getLogger(__name__)


class BaisonE3AdapterStandardInterface(BaseInterface):
    """
    baison-e3 standard 接口实现

    主要 API 接口，提供标准的数据访问能力。

    Example:
        >>> context = ConnectorContext(
        ...     connector_id="test",
        ...     app_software_code="baison_e3",
        ...     base_url="https://api.example.com",
        ...     auth_config={
        ...         "client_id": "xxx",
        ...         "client_secret": "yyy",
        ...     },
        ... )
        >>> interface = BaisonE3AdapterStandardInterface(context, http_client)
        >>> token = await interface.authenticate()
    """

    interface_name = "standard"

    def __init__(self, context: "ConnectorContext", http_client: "HttpClient") -> None:
        super().__init__(context, http_client)
        # 根据实际 API 配置初始化
        self._token_url = self.context.auth_config.get(
            "token_url",
            f"{self.context.base_url}/oauth/token"
        )

    async def authenticate(self) -> dict[str, Any]:
        """
        获取认证凭证

        根据平台的认证方式实现（OAuth2 / API Key / Session 等）

        Returns:
            Token 信息

        Raises:
            BaisonE3AdapterAuthError: 认证失败
        """
        auth_config = self.get_auth_config()

        # TODO: 根据实际平台的认证方式实现
        # 示例：OAuth2 客户端凭证模式
        client_id = auth_config.get("client_id")
        client_secret = auth_config.get("client_secret")

        if not client_id or not client_secret:
            raise BaisonE3AdapterAuthError(
                "Missing required credentials",
                details={"missing": [k for k in ["client_id", "client_secret"] if not auth_config.get(k)]}
            )

        try:
            response = await self.http_client.post(
                self._token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )

            if isinstance(response, dict) and "access_token" in response:
                logger.debug("Authentication successful")
                return response

            raise BaisonE3AdapterAuthError(
                "Invalid authentication response",
                details={"response": response},
            )

        except AuthenticationError:
            raise
        except Exception as e:
            raise BaisonE3AdapterAuthError(
                f"Authentication failed: {e}",
                details={"error": str(e)},
            ) from e

    async def list_objects(
        self,
        object_type: str,
        filters: dict[str, Any] | None = None,
        page_size: int = 100,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        列表查询（自动翻页）

        Args:
            object_type: 对象类型，如 "orders", "products"
            filters: 过滤条件
            page_size: 每页大小

        Yields:
            单条记录
        """
        filters = filters or {}
        page = 1
        has_more = True

        while has_more:
            params = {
                "page": page,
                "page_size": page_size,
                **filters,
            }

            try:
                # TODO: 根据实际 API 路径调整
                response = await self.http_client.get(
                    f"/api/v1/{object_type}",
                    params=params,
                )

                # TODO: 根据实际响应格式调整解析逻辑
                items = response.get("data", [])
                pagination = response.get("pagination", {})

                for item in items:
                    yield item

                # 判断是否还有更多数据
                total = pagination.get("total", 0)
                current_count = page * page_size
                has_more = current_count < total and len(items) == page_size
                page += 1

            except Exception as e:
                logger.error("Failed to fetch %s list: %s", object_type, e)
                raise BaisonE3AdapterAPIError(
                    f"Failed to list {object_type}",
                    details={"object_type": object_type, "page": page, "error": str(e)},
                ) from e

    async def get_object(self, object_type: str, object_id: str) -> dict[str, Any]:
        """
        获取单个对象

        Args:
            object_type: 对象类型
            object_id: 对象 ID

        Returns:
            对象数据

        Raises:
            NotFoundError: 对象不存在
        """
        try:
            # TODO: 根据实际 API 路径调整
            response = await self.http_client.get(f"/api/v1/{object_type}/{object_id}")
            return response.get("data", response)
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise NotFoundError(
                    f"{object_type} not found",
                    resource_type=object_type,
                    resource_id=object_id,
                ) from e
            raise BaisonE3AdapterAPIError(
                f"Failed to get {object_type}",
                details={"object_type": object_type, "object_id": object_id},
            ) from e

    async def create_object(self, object_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        创建对象

        Args:
            object_type: 对象类型
            data: 对象数据

        Returns:
            创建后的对象

        Raises:
            ValidationError: 数据验证失败
        """
        try:
            # TODO: 根据实际 API 路径调整
            response = await self.http_client.post(
                f"/api/v1/{object_type}",
                json=data,
            )
            return response.get("data", response)
        except Exception as e:
            if "400" in str(e) or "validation" in str(e).lower():
                raise ValidationError(
                    f"Invalid data for {object_type}",
                    details={"object_type": object_type, "data": data, "error": str(e)},
                ) from e
            raise BaisonE3AdapterAPIError(
                f"Failed to create {object_type}",
                details={"object_type": object_type},
            ) from e

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            True: 连接正常
            False: 连接异常
        """
        try:
            await self.authenticate()
            return True
        except Exception as e:
            logger.warning("Health check failed: %s", e)
            return False


__all__ = ["BaisonE3AdapterStandardInterface"]