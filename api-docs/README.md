# 百胜E3 (Baison E3) API 文档

> 本目录收录百胜E3 开放平台官方 API 的参考资料与适配器使用说明。

## 官方文档

| 资源 | 地址 | 说明 |
|------|------|------|
| 官方文档中心 | <https://openapi.baison.net/index.html#/doc> | 百胜E3 开放平台接口文档 |
| 本目录接口清单 | `apis_list.json` | 139 个接口清单 |
| 认证与签名指南 | `../docs/auth-guide.md` | 已验证的 MD5 签名算法与连接器信息 |
| 开发规范 | `../docs/prompt.md` | 适配器开发任务说明 |

## 本目录文件说明

```
api-docs/
├── README.md                      # 本文件（文档入口）
├── apis_list.json                 # 139 个 API 清单
├── postman-collection.json        # Postman 测试集合
├── postman-pre-request-script.js  # Postman 自动签名脚本
└── openapi.yaml                   # OpenAPI/Swagger 定义（待补充）
```

---

## 接口概览

截至文档更新时，百胜E3 开放平台共提供 **139 个接口**，分为以下大类：

| 大类 | 涉及子模块 | 常见用途 |
|------|-----------|---------|
| 基础 API | shop、region、cangku、shipping、suppliers、fxs、qudao、user | 门店、仓库、渠道、会员等主数据 |
| 商品 API | goods_info、basic、platform_goods、taocan、barcode、uniquecode | 商品资料、SKU、颜色尺码等品牌档案 |
| 采购 API | cgjrd、cgtzd、cgthtzd、cgthjrd、spjhd、cktcd | 采购通知、进货单、退货单 |
| 批发 API | pftzd、pfxhd、pfthtzd、pfthd | 批发通知、批发销售/退货 |
| 订单 API | order 系列 | 销售订单、订单详情、发货、对账 |
| 售后 API | order_refund、return | 退货退款、快速入库 |
| 库存 API | kc、kcdj、crtzd、zzcx | 库存查询、出入库单据、调拨 |
| 财务 API | bill | 对账费用单等 |
| iPOS API | store/cangku、store/kc、store/order | 门店 POS 销售与库存同步 |

> 完整接口列表请查看本目录下的 `apis_list.json`。

---

## 认证方式

百胜E3 开放平台使用 **AppKey + AppSecret + MD5 签名** 的认证方式，不是 OAuth2。

### 必要参数

| 参数 | 说明 |
|------|------|
| `key` | AppKey，由百胜E3 开放平台应用管理页面获取 |
| `secret` | AppSecret，**仅参与签名，不发送** |
| `version` | 协议版本，固定 `3.0` |
| `requestTime` | 时间戳，格式 `yyyyMMddHHmmss`，GMT+8，允许误差 10 分钟 |
| `serviceType` | API 接口名称，如 `e3oms.base.sd.get` |
| `data` | 业务参数 JSON 字符串 |
| `sign` | MD5 小写签名 |

### 签名算法

```
1. 构建参数对象（包含 secret，仅用于签名）:
   key=APP_KEY
   requestTime=yyyyMMddHHmmss
   secret=APP_SECRET
   version=3.0
   serviceType=API_NAME
   data=JSON_STRING

2. 移除 data 参数

3. 用 http_build_query / urlencode 编码剩余参数:
   key=xxx&requestTime=xxx&secret=xxx&version=3.0&serviceType=xxx

4. 拼接 "&data=" + 原始 JSON 字符串:
   key=xxx&requestTime=xxx&secret=xxx&version=3.0&serviceType=xxx&data={"pageNo":1,"pageSize":2}

5. 对整个字符串做 MD5，结果转小写

6. 最终请求参数中移除 secret（只参与签名，不发送）
```

**Python 示例：**

```python
import hashlib
from urllib.parse import urlencode

params = {
    "key": APP_KEY,
    "requestTime": request_time,
    "secret": APP_SECRET,
    "version": "3.0",
    "serviceType": API_NAME,
}
data = '{"pageNo":1,"pageSize":2}'

sign_str = urlencode(params, doseq=False) + "&data=" + data
sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()  # 小写
```

> ⚠️ **注意**：请求中**不要**带 `format` 和 `sign_method` 参数，否则签名会失败！

详细说明请参阅 [`docs/auth-guide.md`](../docs/auth-guide.md)。

---

## 请求格式

所有接口统一使用 **GET** 请求到以下地址：

```
GET {base_url}/?app_act=api/ec&app_mode=func
    &serviceType=e3oms.base.sd.get
    &key=APP_KEY
    &requestTime=yyyyMMddHHmmss
    &version=3.0
    &data=JSON_STRING
    &sign=MD5_LOWERCASE
```

- `{base_url}` 请替换为你的百胜E3 环境地址（沙箱或生产）。
- `AppKey`、`AppSecret` 请咨询百胜E3 技术支持或实施人员获取。

---

## 响应格式

```json
{
  "status": 1,
  "message": "success",
  "data": [
    {
      "page": [
        {"pageNo": 1, "pageSize": 10, "pageTotal": 5, "totalResult": 42}
      ],
      "sdListGet": [
        {"khdm": "SH001", "khmc": "商店1"}
      ]
    }
  ],
  "requestid": "xxx"
}
```

| 字段 | 说明 |
|------|------|
| `status` | `1` 或 `"api-success"` 表示成功；`-1` 或其他值表示失败 |
| `message` | 操作消息或错误描述 |
| `data` | 响应数据，可能是 `dict` 或 `list`；查询类接口通常包含 `page` 分页信息和列表字段 |
| `requestid` | 请求唯一标识，排错时使用 |

### 常见错误码

| 错误码 | 说明 |
|--------|------|
| `api-success` | 调用成功 |
| `INVALID_PARAMS` | 请求参数错误 |
| `INVALID_REQUEST` | 非法请求 |
| `INVALID_KEY` | 无效的 KEY |
| `INVALID_SIGNATURE` | 无效签名 |
| `INVALID_SERVICE_TYPE` | 不支持的接口名称 |
| `api-server-error` | 服务器错误 |
| `api-server-exception` | 系统内部异常 |
| `api-invalid-parameter-startModified` | 开始时间格式错误 |
| `api-invalid-parameter-pageSize` | 每页数量错误 |

### 适配器异常映射

当百胜E3 返回上述错误时，适配器会转换为以下 Python 异常：

| 触发条件 | 异常类型 |
|---------|---------|
| `INVALID_KEY` / `INVALID_SIGNATURE` / 消息包含"签名" | `BaisonE3AdapterAuthError` |
| 消息同时包含"IP"和"授权" | `BaisonE3AdapterAuthError` |
| 其他 `status != 1` 的业务错误 | `BaisonE3AdapterAPIError` |
| HTTP 请求失败 | `BaisonE3AdapterAPIError` |

---

## 适配器内置对象类型别名

在 `BaisonE3Adapter` 中使用 `list_objects()` / `get_object()` / `invoke()` 时，可以使用以下别名代替完整的 `serviceType`：

### 基础数据

| 别名 | 映射 serviceType | 说明 |
|------|-----------------|------|
| `shop` / `shops` / `sd` | `e3oms.base.sd.get` | 商店/门店 |
| `region` / `regions` | `e3oms.base.region.list.get` | 区域 |
| `shipping` / `shippings` | `e3oms.base.shipping.list.get` | 快递/物流 |
| `user` / `users` / `member` / `members` | `e3oms.base.user.list.get` | 会员/用户 |
| `channel` / `channels` / `qudao` / `qd` | `e3oms.base.qd.get` | 销售渠道 |
| `warehouse` / `warehouses` / `cangku` / `ck` | `e3oms.base.cangku.get` | 仓库 |

### 商品数据

| 别名 | 映射 serviceType | 说明 |
|------|-----------------|------|
| `goods` / `product` / `products` | `e3oms.goods.list.get` | 商品资料 |
| `sku` / `skus` | `e3oms.goods.sku.list.get` | SKU |
| `brand` / `brands` | `e3oms.goods.brand.list.get` | 品牌 |
| `color` / `colors` | `e3oms.goods.color.list.get` | 颜色 |
| `size` / `sizes` | `e3oms.goods.size.list.get` | 尺码 |
| `season` / `seasons` | `e3oms.goods.season.list.get` | 季节 |
| `year` / `years` | `e3oms.goods.year.list.get` | 年份 |
| `series` | `e3oms.goods.series.list.get` | 系列 |
| `cat` / `cats` / `category` / `categories` | `e3oms.goods.cat.list.get` | 分类 |
| `outer_sku` | `e3oms.goods.outer.sku.list.get` | 平台商品 |
| `uniquecode` | `e3oms.goods.uniquecode.detail.get` | 唯一码 |

### 订单与售后

| 别名 | 映射 serviceType | 说明 |
|------|-----------------|------|
| `order` / `orders` | `e3oms.order.list.get` | 订单列表 |
| `order_detail` | `e3oms.order.detail.get` | 订单详情 |
| `order_split` | `e3oms.order.split.list.get` | 订单拆分 |
| `return` / `returns` / `refund` | `e3oms.order.return.list.get` | 退货退款 |
| `tb_refund` | `e3oms.order.tb.refund.get` | 淘宝退款 |

### 采购、批发、财务、iPOS

| 别名 | 映射 serviceType | 说明 |
|------|-----------------|------|
| `purchase_notice` | `e3oms.purchase.cgtzd.get` | 采购通知单 |
| `purchase_return_notice` | `e3oms.purchase.cgthtzd.get` | 采购退货通知单 |
| `purchase_in` | `e3oms.purchase.spjhd.get` | 采购进货单 |
| `purchase_return` | `e3oms.purchase.cktcd.get` | 采购退货出库单 |
| `wholesale_notice` | `e3oms.wholesale.pftzd.get` | 批发通知单 |
| `wholesale_return_notice` | `e3oms.wholesale.pfthtzd.get` | 批发退货通知单 |
| `wholesale_return` | `e3oms.wholesale.pfthd.list.get` | 批发退货单 |
| `wholesale_sale` | `e3oms.wholesale.pfxhd.list.get` | 批发销售单 |
| `dzdfee` | `e3oms.finance.dzdfee.get` | 对账费用单 |
| `ipos_kc` | `e3oms.store.kc.get` | iPOS 库存 |
| `ipos_md_ck` | `e3oms.store.md.cangku.get` | iPOS 门店仓库 |
| `ipos_user_ck` | `e3oms.store.user.cangku.get` | iPOS 用户仓库 |

> 未在别名表中的接口，可以直接传入完整 `serviceType`（例如 `e3oms.order.info.through.goods.sn.get`）调用 `invoke()`。

---

## 适配器公开方法

### `BaisonE3Adapter`

适配器主类，继承自 `BaseAppAdapter`。

#### 构造函数

```python
BaisonE3Adapter(context: ConnectorContext, token_cache=None)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `context` | `ConnectorContext` | 连接器上下文，包含 `base_url`、`auth_config`、`environment` 等 |
| `token_cache` | `Any` | Token 缓存（可选），百胜E3 当前实现未使用 |

#### `auth_config` 格式

```python
{
    "app_key": "你的 AppKey",
    "app_secret": "你的 AppSecret",
}
```

兼容以下别名：`app_key` / `key` / `client_id`、`app_secret` / `secret` / `client_secret`。

#### 方法列表

| 方法 | 签名 | 说明 |
|------|------|------|
| `authenticate` | `() -> dict` | 验证认证配置是否有效 |
| `refresh_token` | `() -> dict` | 同 `authenticate`，保持接口一致性 |
| `test_connection` | `() -> TestConnectionResult` | 测试与百胜E3 的连接 |
| `list_objects` | `(object_type, filters=None, page_size=100) -> AsyncIterator[dict]` | 列表查询，自动分页 |
| `query_objects` | `(object_type, filters=None, page_size=100) -> AsyncIterator[dict]` | `list_objects` 的别名，供工作流节点使用 |
| `get_object` | `(object_type, object_id) -> dict` | 单条查询 |
| `create_object` | `(object_type, data) -> dict` | 创建对象 |
| `invoke` | `(method, object_type, data=None, params=None) -> dict` | 灵活调用任意 serviceType |
| `get_interface_info` | `() -> dict` | 获取当前接口元数据 |

#### `invoke()` 方法说明

`invoke()` 是调用百胜E3 任意接口的通用入口：

```python
# 使用内置别名查询列表
await adapter.invoke("query", "orders", params={"pageNo": 1, "pageSize": 10})

# 使用完整 serviceType
await adapter.invoke(
    "query",
    "e3oms.order.info.through.goods.sn.get",
    params={"goodsSn": "SN12345"}
)

# 创建对象
await adapter.invoke("create", "orders", data={"orderSn": "ORD001", ...})
```

当 `object_type` 包含 `.` 时，会将其视为完整的 `serviceType`，不再查找别名表。

---

## 分页行为

`list_objects()` 和 `query_objects()` 会自动处理分页：

1. 从响应 `data[0].page` 读取 `pageNo`、`pageSize`、`pageTotal`、`totalResult`
2. 自动递增 `pageNo` 直到数据获取完毕
3. `page_size` 最大支持到 `1000`
4. 每条返回记录包含 `_meta` 字段：

```python
{
    "_meta": {
        "page_no": 1,
        "page_size": 100,
        "total_result": 1000,
        "page_total": 10,
        "service_type": "e3oms.order.list.get",
    }
}
```

---

## 可测试的查询接口

开发/测试阶段推荐优先使用以下只读接口：

| 接口 | serviceType |
|------|------------|
| 商店列表 | `e3oms.base.sd.get` |
| 区域列表 | `e3oms.base.region.list.get` |
| 快递列表 | `e3oms.base.shipping.list.get` |
| 会员列表 | `e3oms.base.user.list.get` |
| 渠道列表 | `e3oms.base.qd.get` |
| 仓库列表 | `e3oms.base.cangku.get` |
| 商品列表 | `e3oms.goods.list.get` |
| SKU 列表 | `e3oms.goods.sku.list.get` |
| 订单列表 | `e3oms.order.list.get` |
| 订单详情 | `e3oms.order.detail.get` |
| 退货列表 | `e3oms.order.return.list.get` |

> ⚠️ **测试时只调用查询接口（GET / list.get），不要测试写入接口，以免产生脏数据！**

---

## 调试工具

### Postman / APIPost

- 导入：`postman-collection.json`
- 自动签名脚本：`postman-pre-request-script.js`，复制到 Pre-request Script 标签页即可。

使用前请在 Postman 环境变量中设置 `baison_app_key` 和 `baison_app_secret`。

详细用法请参阅 [`docs/auth-guide.md`](../docs/auth-guide.md)。

### Python 适配器示例

```python
import asyncio
from qdata_adapter import ConnectorContext
from qdata_adapter_baison_e3 import BaisonE3Adapter

async def main():
    context = ConnectorContext(
        connector_id="demo",
        app_software_code="baison_e3",
        base_url="https://your-baison-e3-domain/webopm/web/",
        auth_config={
            "app_key": "你的 AppKey",
            "app_secret": "你的 AppSecret",
        },
    )
    adapter = BaisonE3Adapter(context)

    result = await adapter.test_connection()
    print(result.success, result.message)

    async for shop in adapter.list_objects("shops", page_size=5):
        print(shop)

asyncio.run(main())
```

> `base_url`、`AppKey`、`AppSecret` 请咨询百胜E3 技术支持或实施人员获取。

更多用法请参考 `examples/quickstart.py` 与项目 `README.md`。

---

## 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-06-09 | 0.1.0 | 补全真实百胜E3 API 认证、签名、响应格式、别名映射与适配器 API 参考 |
