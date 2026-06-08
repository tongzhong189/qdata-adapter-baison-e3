"""
BaisonE3Adapter

适配器主类 - 组合器模式实现
单一接口适配器实现
"""

from __future__ import annotations

import logging
import time
from typing import Any, AsyncIterator

from qdata_adapter import BaseAppAdapter
from qdata_adapter.context import ConnectorContext
from qdata_adapter.results import TestConnectionResult

from qdata_adapter_baison_e3.interfaces.base import BaseInterface
from qdata_adapter_baison_e3.interfaces.standard import BaisonE3AdapterStandardInterface

logger = logging.getLogger(__name__)


class BaisonE3Adapter(BaseAppAdapter):
    """
    baison-e3 适配器
    标准适配器实现，基于 standard 接口

    Example:
        >>> context = ConnectorContext(
        ...     connector_id="my-connector",
        ...     app_software_code="baison_e3",
        ...     base_url="https://api.example.com",
        ...     auth_config={"client_id": "xxx", "client_secret": "yyy"},
        ... )
        >>> adapter = BaisonE3Adapter(context)
        >>> result = await adapter.test_connection()
    """

    app_code = "baison_e3"
    adapter_version = "0.1.0"

    def __init__(self, context: ConnectorContext, token_cache: Any = None) -> None:
        """
        初始化适配器

        Args:
            context: 连接器上下文
            token_cache: Token 缓存（可选）

        Note:
            context.settings.interface 控制接口路由：
            - "standard"（默认）
            - "enterprise"（如启用双接口）
        """
        super().__init__(context, token_cache)
        self._interface = self._resolve_interface()
        logger.debug(
            "Initialized BaisonE3Adapter with %s interface",
            self._interface.interface_name
        )

    def _resolve_interface(self) -> BaseInterface:
        """
        根据 settings 路由到对应的接口实现

        Returns:
            接口实现实例
        """
        # 单一接口模式
        return BaisonE3AdapterStandardInterface(
            self.context, self.http_client
        )

    async def authenticate(self) -> dict[str, Any]:
        """
        获取认证凭证

        委托给当前接口实现
        """
        return await self._interface.authenticate()

    async def refresh_token(self) -> dict[str, Any]:
        """
        刷新认证凭证

        委托给当前接口实现
        """
        # 对于大多数接口，refresh 与 authenticate 相同
        return await self._interface.authenticate()

    async def list_objects(
        self,
        object_type: str,
        filters: dict[str, Any] | None = None,
        page_size: int = 100,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        列表查询

        委托给当前接口实现
        """
        async for item in self._interface.list_objects(object_type, filters, page_size):
            yield item

    async def query_objects(
        self,
        object_type: str,
        filters: dict[str, Any] | None = None,
        page_size: int = 100,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        查询对象列表（工作流节点优先使用此方法）

        这是 list_objects() 的别名，用于与工作流节点的契约匹配。
        工作流节点首先查找 query_objects()，其次才是 list_objects()。

        Args:
            object_type: 对象类型
            filters: 过滤条件
            page_size: 每页大小

        Yields:
            单条记录字典

        Example:
            >>> async for item in adapter.query_objects("orders", {"status": "pending"}):
            ...     print(item["id"])
        """
        async for item in self._interface.list_objects(object_type, filters, page_size):
            yield item

    async def get_object(self, object_type: str, object_id: str) -> dict[str, Any]:
        """
        获取单个对象

        委托给当前接口实现
        """
        return await self._interface.get_object(object_type, object_id)

    async def create_object(self, object_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        创建对象

        委托给当前接口实现
        """
        return await self._interface.create_object(object_type, data)

    async def invoke(
        self,
        method: str,
        object_type: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        统一的 API 调用方法

        对于拥有成百上千个 API 的平台，此方法提供灵活的统一调用入口。
        支持任意 API 方法（query/get/create/update/delete 等），
        而不局限于 list_objects/get_object/create_object 三种操作。

        默认实现会路由到对应的标准方法，子类可以覆盖实现更复杂的逻辑。

        Args:
            method: API 方法名，如 "query", "get", "create", "update", "delete"
            object_type: 对象类型，如 "orders", "products"
            data: 请求体数据（用于 create/update 等）
            params: 查询参数（用于 query/get 等）

        Returns:
            API 响应数据

        Raises:
            BaisonE3AdapterAuthError: 认证失败
            BaisonE3AdapterAPIError: API 调用失败
            NotImplementedError: 方法不支持

        Example:
            >>> # 查询列表
            >>> result = await adapter.invoke(
            ...     "query", "orders",
            ...     params={"status": "pending"}
            ... )
            >>>
            >>> # 获取单条
            >>> result = await adapter.invoke(
            ...     "get", "orders",
            ...     params={"id": "ORD001"}
            ... )
            >>>
            >>> # 创建对象
            >>> result = await adapter.invoke(
            ...     "create", "orders",
            ...     data={"customer": "张三", "amount": 100}
            ... )
            >>>
            >>> # 调用平台特有 API
            >>> result = await adapter.invoke(
            ...     "jky.goods.batchupdateflag",
            ...     "goods",
            ...     data={"goods_ids": ["1", "2"], "flag": 1}
            ... )
        """
        # 委托给接口实现
        if hasattr(self._interface, 'invoke'):
            return await self._interface.invoke(method, object_type, data, params)

        # 默认路由到标准方法
        if method in ("list", "query"):
            results = []
            async for item in self._interface.list_objects(
                object_type, filters=params, page_size=100
            ):
                results.append(item)
            return {"data": results, "total": len(results)}

        elif method == "get":
            object_id = params.get("id") if params else None
            if not object_id:
                raise ValueError("'get' method requires params['id']")
            result = await self._interface.get_object(object_type, object_id)
            return {"data": result}

        elif method == "create":
            if not data:
                raise ValueError("'create' method requires data")
            result = await self._interface.create_object(object_type, data)
            return {"data": result}

        else:
            raise NotImplementedError(
                f"Method '{method}' not implemented in interface. "
                f"Please override invoke() in your interface class or "
                f"implement a custom method handler."
            )

    async def test_connection(self) -> TestConnectionResult:
        """
        测试连接

        检查与 baison-e3 平台的连接是否正常

        Returns:
            连接测试结果
        """
        import time

        start_time = time.time()

        try:
            if await self._interface.health_check():
                return TestConnectionResult.connected(
                    message=f"baison-e3 连接成功",
                    duration_ms=int((time.time() - start_time) * 1000),
                    metadata={
                        "interface": self._interface.interface_name,
                        "base_url": self.context.base_url,
                    },
                )
            else:
                return TestConnectionResult.network_error(
                    message="健康检查失败",
                    duration_ms=int((time.time() - start_time) * 1000),
                )

        except Exception as e:
            logger.error("Connection test failed: %s", e)
            return TestConnectionResult.network_error(
                message=str(e),
                duration_ms=int((time.time() - start_time) * 1000),
                details={"error": str(e)},
            )

    def get_interface_info(self) -> dict[str, Any]:
        """
        获取当前接口信息

        Returns:
            接口信息字典
        """
        return {
            "interface_name": self._interface.interface_name,
            "available_interfaces": ["standard"],
            "adapter_version": self.adapter_version,
            "app_code": self.app_code,
        }


__all__ = ["BaisonE3Adapter"]