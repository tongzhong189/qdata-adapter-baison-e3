"""
baison-e3 standard 接口实现

百胜E3 开放平台适配器，基于 AppKey + AppSecret + MD5 签名认证。
签名规则参考 PHP BaisonSDK：
  1. 参数: key / requestTime / secret / version / serviceType / data
  2. 签名时先移除 data
  3. http_build_query 编码剩余参数
  4. 拼接 "&data=" + 原始 JSON
  5. MD5（小写）
  6. 最终请求中不发送 secret
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, AsyncIterator
from urllib.parse import urlencode

from qdata_adapter.exceptions import NotFoundError, ValidationError

from qdata_adapter_baison_e3.exceptions import (
    BaisonE3AdapterAPIError,
    BaisonE3AdapterAuthError,
)
from qdata_adapter_baison_e3.interfaces.base import BaseInterface

if TYPE_CHECKING:
    from qdata_adapter.client import HttpClient
    from qdata_adapter.context import ConnectorContext

logger = logging.getLogger(__name__)

# object_type -> serviceType 映射（仅查询类接口）
_LIST_OBJECT_TYPE_MAP: dict[str, str] = {
    # 基础API
    "shop": "e3oms.base.sd.get",
    "shops": "e3oms.base.sd.get",
    "sd": "e3oms.base.sd.get",
    "region": "e3oms.base.region.list.get",
    "regions": "e3oms.base.region.list.get",
    "shipping": "e3oms.base.shipping.list.get",
    "shippings": "e3oms.base.shipping.list.get",
    "user": "e3oms.base.user.list.get",
    "users": "e3oms.base.user.list.get",
    "member": "e3oms.base.user.list.get",
    "members": "e3oms.base.user.list.get",
    "channel": "e3oms.base.qd.get",
    "channels": "e3oms.base.qd.get",
    "qudao": "e3oms.base.qd.get",
    "qd": "e3oms.base.qd.get",
    "warehouse": "e3oms.base.cangku.get",
    "warehouses": "e3oms.base.cangku.get",
    "cangku": "e3oms.base.cangku.get",
    "ck": "e3oms.base.cangku.get",
    # 商品API
    "goods": "e3oms.goods.list.get",
    "product": "e3oms.goods.list.get",
    "products": "e3oms.goods.list.get",
    "sku": "e3oms.goods.sku.list.get",
    "skus": "e3oms.goods.sku.list.get",
    "brand": "e3oms.goods.brand.list.get",
    "brands": "e3oms.goods.brand.list.get",
    "color": "e3oms.goods.color.list.get",
    "colors": "e3oms.goods.color.list.get",
    "size": "e3oms.goods.size.list.get",
    "sizes": "e3oms.goods.size.list.get",
    "season": "e3oms.goods.season.list.get",
    "seasons": "e3oms.goods.season.list.get",
    "year": "e3oms.goods.year.list.get",
    "years": "e3oms.goods.year.list.get",
    "series": "e3oms.goods.series.list.get",
    "cat": "e3oms.goods.cat.list.get",
    "cats": "e3oms.goods.cat.list.get",
    "category": "e3oms.goods.cat.list.get",
    "categories": "e3oms.goods.cat.list.get",
    "fjsx": "e3oms.goods.fjsx.list.get",
    "bzdw": "e3oms.goods.bzdw.list.get",
    "taocan": "e3oms.goods.taocan.list.get",
    "barcode": "e3oms.goods.barcodes.add",  # 无查询接口
    "uniquecode": "e3oms.goods.uniquecode.detail.get",
    "outer_sku": "e3oms.goods.outer.sku.list.get",
    # 订单API
    "order": "e3oms.order.list.get",
    "orders": "e3oms.order.list.get",
    "order_detail": "e3oms.order.detail.get",
    "order_split": "e3oms.order.split.list.get",
    "order_qh": "e3oms.order.qh.list.get",
    "order_cklsz": "e3oms.order.cklsz.list.get",
    "order_dzd": "e3oms.order.dzd.list.get",
    "order_jhd": "e3oms.order.jhd.get",
    # 售后API
    "return": "e3oms.order.return.list.get",
    "returns": "e3oms.order.return.list.get",
    "refund": "e3oms.order.return.list.get",
    "tb_refund": "e3oms.order.tb.refund.get",
    # 采购API
    "purchase_notice": "e3oms.purchase.cgtzd.get",
    "purchase_return_notice": "e3oms.purchase.cgthtzd.get",
    "purchase_in": "e3oms.purchase.spjhd.get",
    "purchase_return": "e3oms.purchase.cktcd.get",
    # 批发API
    "wholesale_notice": "e3oms.wholesale.pftzd.get",
    "wholesale_return_notice": "e3oms.wholesale.pfthtzd.get",
    "wholesale_return": "e3oms.wholesale.pfthd.list.get",
    "wholesale_sale": "e3oms.wholesale.pfxhd.list.get",
    # 财务API
    "dzdfee": "e3oms.finance.dzdfee.get",
    # iPOS
    "ipos_kc": "e3oms.store.kc.get",
    "ipos_md_ck": "e3oms.store.md.cangku.get",
    "ipos_user_ck": "e3oms.store.user.cangku.get",
}


class BaisonE3AdapterStandardInterface(BaseInterface):
    """
    baison-e3 standard 接口实现

    百胜E3 开放平台适配器，基于 PHP BaisonSDK 的签名规则：
      - AppKey / AppSecret / MD5 小写签名
      - http_build_query 编码 + &data= 拼接
      - secret 只参与签名，不发送
    """

    interface_name = "standard"

    def __init__(self, context: "ConnectorContext", http_client: "HttpClient") -> None:
        super().__init__(context, http_client)
        auth = self.get_auth_config()
        self._app_key = auth.get("app_key") or auth.get("key") or auth.get("client_id")
        self._app_secret = auth.get("app_secret") or auth.get("secret") or auth.get("client_secret")

        if not self._app_key or not self._app_secret:
            raise BaisonE3AdapterAuthError(
                "Missing app_key or app_secret in auth_config",
                details={"missing": [k for k in ("app_key", "app_secret") if not auth.get(k)]},
            )

    # ── 签名与请求构建 ──

    @staticmethod
    def _generate_sign(
        params: dict[str, Any],
        app_secret: str,
    ) -> tuple[str, str]:
        """
        百胜E3 MD5 签名算法（参考 PHP BaisonSDK）

        1. 先移除 data 参数
        2. 用 http_build_query 编码剩余参数
        3. 拼接 "&data=" + 原始 JSON
        4. MD5 加密，结果小写

        Returns:
            (签名字符串原文, 签名结果)
        """
        params = dict(params)
        data = params.pop("data")
        sign_str = urlencode(params, doseq=False) + "&data=" + data
        import hashlib

        sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()
        return sign_str, sign

    def _build_request_data(self, service_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """构建带签名的请求参数"""
        tz = timezone(timedelta(hours=8))
        request_time = datetime.now(tz).strftime("%Y%m%d%H%M%S")
        data_str = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

        # 签名时包含 secret，请求中不发送
        params: dict[str, Any] = {
            "key": self._app_key,
            "requestTime": request_time,
            "secret": self._app_secret,
            "version": "3.0",
            "serviceType": service_type,
            "data": data_str,
        }

        _, params["sign"] = self._generate_sign(params, self._app_secret)

        # 移除 secret，不发送到服务端
        params.pop("secret", None)
        return params

    async def _call_api(
        self,
        service_type: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        调用百胜E3 API

        Returns:
            原始响应字典
        """
        data = data or {}
        request_data = self._build_request_data(service_type, data)

        query_params = {
            "app_act": "api/ec",
            "app_mode": "func",
            **request_data,
        }

        try:
            response = await self.http_client.get("/", params=query_params)
        except Exception as e:
            raise BaisonE3AdapterAPIError(
                f"API request failed: {e}",
                details={"service_type": service_type, "error": str(e)},
            ) from e

        # 兼容 text/html 但内容为 JSON 的情况
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except json.JSONDecodeError as e:
                raise BaisonE3AdapterAPIError(
                    "Unexpected response format",
                    details={"service_type": service_type, "response": response},
                ) from e

        if not isinstance(response, dict):
            raise BaisonE3AdapterAPIError(
                "Unexpected response format",
                details={"service_type": service_type, "response": response},
            )

        status = response.get("status")
        # 百胜E3 错误状态可能是 -1、字符串如 "INVALID_SIGNATURE"、或 "INVALID_REQUEST"
        is_error = status not in (1, "1", "api-success")
        if is_error:
            msg = response.get("message", "Unknown error")
            if "IP" in msg and "授权" in msg:
                raise BaisonE3AdapterAuthError(
                    f"IP authorization required: {msg}",
                    details={"service_type": service_type, "response": response},
                )
            if "签名" in msg or "sign" in str(status).lower():
                raise BaisonE3AdapterAuthError(
                    f"Invalid signature: {msg}",
                    details={"service_type": service_type, "response": response},
                )
            raise BaisonE3AdapterAPIError(
                msg,
                api_code=str(status),
                response_body=response,
                details={"service_type": service_type},
            )

        return response

    # ── BaseInterface 实现 ──

    async def authenticate(self) -> dict[str, Any]:
        """
        验证认证配置是否有效

        通过调用一个简单的查询接口来验证配置。
        """
        try:
            resp = await self._call_api("e3oms.base.sd.get", {"pageNo": 1, "pageSize": 1})
            return {"authenticated": True, "app_key": self._app_key}
        except BaisonE3AdapterAPIError as e:
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
        列表查询，自动处理翻页

        object_type 支持两种形式：
        1. 内置别名，如 "orders", "goods", "shops" 等
        2. 直接传入 serviceType，如 "e3oms.order.list.get"
        """
        filters = filters or {}
        service_type = self._resolve_service_type(object_type)

        page_no = 1
        has_more = True

        while has_more:
            data = {
                "pageNo": page_no,
                "pageSize": min(page_size, 1000),
                **filters,
            }

            resp = await self._call_api(service_type, data)
            resp_data = resp.get("data", [])

            # 百胜E3 实际响应中 data 可能是 dict 或 list
            if isinstance(resp_data, dict):
                first_item = resp_data
            elif isinstance(resp_data, list) and resp_data:
                first_item = resp_data[0]
            else:
                break

            if not isinstance(first_item, dict):
                break

            # 分页信息
            page_info = first_item.get("page", {})
            if isinstance(page_info, list) and page_info:
                page_info = page_info[0]
            page_info = page_info or {}

            # 提取列表字段（排除已知的元数据字段）
            meta_keys = {"page"}
            list_keys = [k for k in first_item.keys() if k not in meta_keys]

            items: list[dict[str, Any]] = []
            for lk in list_keys:
                val = first_item.get(lk)
                if isinstance(val, list):
                    items = val
                    break

            for item in items:
                if isinstance(item, dict):
                    item["_meta"] = {
                        "page_no": page_no,
                        "page_size": page_size,
                        "total_result": page_info.get("totalResult"),
                        "page_total": page_info.get("pageTotal"),
                        "service_type": service_type,
                    }
                    yield item

            total_result = page_info.get("totalResult")
            page_total = page_info.get("pageTotal")

            if page_total is not None:
                has_more = page_no < page_total
            elif total_result is not None:
                has_more = len(items) == page_size and (page_no * page_size) < total_result
            else:
                has_more = len(items) == page_size

            page_no += 1

    async def get_object(self, object_type: str, object_id: str) -> dict[str, Any]:
        """获取单个对象"""
        filters: dict[str, Any] = {}
        service_type = self._resolve_service_type(object_type)

        id_field_map: dict[str, str] = {
            "e3oms.base.sd.get": "sddm",
            "e3oms.goods.list.get": "goodsSn",
            "e3oms.goods.sku.list.get": "sku",
            "e3oms.order.list.get": "orderSn",
            "e3oms.base.user.list.get": "khdm",
            "e3oms.base.qd.get": "qddm",
            "e3oms.base.cangku.get": "ckdm",
        }

        id_field = id_field_map.get(service_type)
        if id_field:
            filters[id_field] = object_id

        filters["pageNo"] = 1
        filters["pageSize"] = 10

        resp = await self._call_api(service_type, filters)
        resp_data = resp.get("data", [])
        if not resp_data:
            raise NotFoundError(
                f"{object_type} not found",
                resource_type=object_type,
                resource_id=object_id,
            )

        if isinstance(resp_data, dict):
            first_item = resp_data
        elif isinstance(resp_data, list) and resp_data:
            first_item = resp_data[0]
        else:
            raise NotFoundError(
                f"{object_type} not found",
                resource_type=object_type,
                resource_id=object_id,
            )

        if not isinstance(first_item, dict):
            raise NotFoundError(
                f"{object_type} not found",
                resource_type=object_type,
                resource_id=object_id,
            )

        meta_keys = {"page"}
        for k, v in first_item.items():
            if k not in meta_keys and isinstance(v, list) and v:
                if id_field:
                    for item in v:
                        if isinstance(item, dict) and str(item.get(id_field, "")) == str(object_id):
                            return item
                first_record = v[0]
                if isinstance(first_record, dict):
                    return first_record

        raise NotFoundError(
            f"{object_type} not found",
            resource_type=object_type,
            resource_id=object_id,
        )

    async def create_object(self, object_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """创建对象"""
        service_type = self._resolve_add_service_type(object_type)
        resp = await self._call_api(service_type, data)
        return resp

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            await self._call_api("e3oms.base.sd.get", {"pageNo": 1, "pageSize": 1})
            return True
        except Exception as e:
            logger.warning("Health check failed: %s", e)
            return False

    # ── invoke 扩展 ──

    async def invoke(
        self,
        method: str,
        object_type: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """直接调用百胜E3 API"""
        if "." in object_type:
            service_type = object_type
        else:
            if method in ("list", "query", "get"):
                service_type = self._resolve_service_type(object_type)
            elif method == "create":
                service_type = self._resolve_add_service_type(object_type)
            else:
                raise NotImplementedError(
                    f"Method '{method}' not supported for object_type '{object_type}'"
                )

        request_data = {**(params or {}), **(data or {})}
        return await self._call_api(service_type, request_data)

    # ── 内部工具 ──

    def _resolve_service_type(self, object_type: str) -> str:
        """将 object_type 解析为 serviceType"""
        if "." in object_type:
            return object_type
        service_type = _LIST_OBJECT_TYPE_MAP.get(object_type)
        if not service_type:
            raise ValidationError(
                f"Unknown object_type: {object_type}",
                details={"object_type": object_type, "known_types": list(_LIST_OBJECT_TYPE_MAP.keys())},
            )
        return service_type

    def _resolve_add_service_type(self, object_type: str) -> str:
        """将 object_type 解析为对应的 add serviceType"""
        list_service = self._resolve_service_type(object_type)
        add_service = list_service.replace(".list.get", ".add").replace(".get", ".add")
        if add_service == list_service:
            raise ValidationError(
                f"Cannot infer add service_type for {object_type}",
                details={"object_type": object_type},
            )
        return add_service


__all__ = ["BaisonE3AdapterStandardInterface"]
