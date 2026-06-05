"""
适配器测试

测试 BaisonE3Adapter 的核心功能
基于 pytest-httpx mock 百胜E3 的签名请求/响应
"""

from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from qdata_adapter_baison_e3 import BaisonE3Adapter
from qdata_adapter import ConnectorContext


class TestBaisonE3Adapter:
    """BaisonE3Adapter 测试类"""

    @pytest.mark.asyncio
    async def test_adapter_initialization(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
    ) -> None:
        """测试适配器初始化"""
        adapter = BaisonE3Adapter(standard_context, mock_token_cache)

        assert adapter.app_code == "baison_e3"
        assert adapter.adapter_version == "0.1.0"
        assert adapter.context == standard_context

    @pytest.mark.asyncio
    async def test_authenticate_success(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试认证（通过商店列表接口验证配置）"""
        httpx_mock.add_response(
            method="GET",
            json={"status": 1, "message": "success", "data": [{"sdListGet": []}]},
        )

        adapter = BaisonE3Adapter(standard_context, mock_token_cache)
        result = await adapter.authenticate()

        assert result["authenticated"] is True
        assert result["app_key"] == "test-app-key"

    @pytest.mark.asyncio
    async def test_authenticate_failure(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试认证失败"""
        httpx_mock.add_response(
            method="GET",
            json={"status": -1, "message": "签名错误", "data": ""},
        )

        adapter = BaisonE3Adapter(standard_context, mock_token_cache)
        from qdata_adapter_baison_e3.exceptions import BaisonE3AdapterAuthError
        with pytest.raises(BaisonE3AdapterAuthError):
            await adapter.authenticate()

    @pytest.mark.asyncio
    async def test_list_objects_shops(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试列表查询 - 商店"""
        httpx_mock.add_response(
            method="GET",
            json={
                "status": 1,
                "message": "success",
                "data": [{
                    "page": [{"pageNo": 1, "pageSize": 5, "pageTotal": 1, "totalResult": 2}],
                    "sdListGet": [
                        {"khdm": "SH001", "khmc": "商店1"},
                        {"khdm": "SH002", "khmc": "商店2"},
                    ],
                }],
            },
        )

        adapter = BaisonE3Adapter(standard_context, mock_token_cache)
        records = []
        async for record in adapter.list_objects("shops", page_size=5):
            records.append(record)

        assert len(records) == 2
        assert records[0]["khdm"] == "SH001"
        assert records[1]["khmc"] == "商店2"
        assert records[0]["_meta"]["service_type"] == "e3oms.base.sd.get"

    @pytest.mark.asyncio
    async def test_list_objects_pagination(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试列表查询 - 自动翻页"""
        # 第一页
        httpx_mock.add_response(
            method="GET",
            json={
                "status": 1,
                "message": "success",
                "data": [{
                    "page": [{"pageNo": 1, "pageSize": 2, "pageTotal": 2, "totalResult": 3}],
                    "goodsListGet": [
                        {"goodsSn": "G001", "goodsName": "商品1"},
                        {"goodsSn": "G002", "goodsName": "商品2"},
                    ],
                }],
            },
        )
        # 第二页
        httpx_mock.add_response(
            method="GET",
            json={
                "status": 1,
                "message": "success",
                "data": [{
                    "page": [{"pageNo": 2, "pageSize": 2, "pageTotal": 2, "totalResult": 3}],
                    "goodsListGet": [
                        {"goodsSn": "G003", "goodsName": "商品3"},
                    ],
                }],
            },
        )

        adapter = BaisonE3Adapter(standard_context, mock_token_cache)
        records = []
        async for record in adapter.list_objects("goods", page_size=2):
            records.append(record)

        assert len(records) == 3
        assert records[2]["goodsSn"] == "G003"

    @pytest.mark.asyncio
    async def test_get_object(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试单条查询"""
        httpx_mock.add_response(
            method="GET",
            json={
                "status": 1,
                "message": "success",
                "data": [{
                    "page": [{"pageNo": 1, "pageSize": 10, "pageTotal": 1, "totalResult": 1}],
                    "sdListGet": [
                        {"khdm": "SH001", "khmc": "商店1", "lxr": "张三"},
                    ],
                }],
            },
        )

        adapter = BaisonE3Adapter(standard_context, mock_token_cache)
        result = await adapter.get_object("shops", "SH001")

        assert result["khdm"] == "SH001"
        assert result["khmc"] == "商店1"

    @pytest.mark.asyncio
    async def test_get_object_not_found(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试单条查询 - 未找到"""
        httpx_mock.add_response(
            method="GET",
            json={
                "status": 1,
                "message": "success",
                "data": [{
                    "page": [{"pageNo": 1, "pageSize": 10, "pageTotal": 1, "totalResult": 0}],
                    "sdListGet": [],
                }],
            },
        )

        adapter = BaisonE3Adapter(standard_context, mock_token_cache)
        from qdata_adapter.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            await adapter.get_object("shops", "NOT_EXIST")

    @pytest.mark.asyncio
    async def test_invoke_direct_service_type(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试 invoke 直接传入 serviceType"""
        httpx_mock.add_response(
            method="GET",
            json={
                "status": 1,
                "message": "success",
                "data": [{
                    "page": [{"pageNo": 1, "pageSize": 10, "pageTotal": 1, "totalResult": 1}],
                    "orderListGets": [[
                        {"order_sn": "O001", "total_amount": 100},
                    ]],
                }],
            },
        )

        adapter = BaisonE3Adapter(standard_context, mock_token_cache)
        result = await adapter.invoke(
            "query", "e3oms.order.list.get",
            params={"pageNo": 1, "pageSize": 10},
        )

        assert result["status"] == 1
        assert "data" in result

    @pytest.mark.asyncio
    async def test_test_connection_success(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试连接测试 - 成功场景"""
        httpx_mock.add_response(
            method="GET",
            json={"status": 1, "message": "success", "data": [{"sdListGet": []}]},
        )

        adapter = BaisonE3Adapter(standard_context, mock_token_cache)
        result = await adapter.test_connection()

        assert result.success is True
        assert result.status == "connected"

    @pytest.mark.asyncio
    async def test_test_connection_failure(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试连接测试 - 失败场景"""
        # HttpClient 会重试 3 次，需要注册多个响应
        for _ in range(4):
            httpx_mock.add_response(
                method="GET",
                status_code=500,
                json={"error": "internal server error"},
            )

        adapter = BaisonE3Adapter(standard_context, mock_token_cache)
        result = await adapter.test_connection()

        assert result.success is False

    @pytest.mark.asyncio
    async def test_query_objects_alias(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试 query_objects 方法（工作流节点优先使用）"""
        httpx_mock.add_response(
            method="GET",
            json={
                "status": 1,
                "message": "success",
                "data": [{
                    "page": [{"pageNo": 1, "pageSize": 50, "pageTotal": 1, "totalResult": 2}],
                    "qdListGet": [
                        {"khdm": "U001", "khmc": "会员1"},
                        {"khdm": "U002", "khmc": "会员2"},
                    ],
                }],
            },
        )

        adapter = BaisonE3Adapter(standard_context, mock_token_cache)
        records = []
        async for record in adapter.query_objects("members", page_size=50):
            records.append(record)

        assert len(records) == 2
        assert records[0]["khdm"] == "U001"

    @pytest.mark.asyncio
    async def test_api_error_response(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试 API 返回业务错误"""
        httpx_mock.add_response(
            method="GET",
            json={"status": -1, "message": "参数错误", "data": ""},
        )

        adapter = BaisonE3Adapter(standard_context, mock_token_cache)
        from qdata_adapter_baison_e3.exceptions import BaisonE3AdapterAPIError
        with pytest.raises(BaisonE3AdapterAPIError):
            async for _ in adapter.list_objects("shops"):
                pass

    @pytest.mark.asyncio
    async def test_get_interface_info(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
    ) -> None:
        """测试获取接口信息"""
        adapter = BaisonE3Adapter(standard_context, mock_token_cache)
        info = adapter.get_interface_info()

        assert "interface_name" in info
        assert "available_interfaces" in info
        assert info["adapter_version"] == "0.1.0"
        assert info["app_code"] == "baison_e3"
