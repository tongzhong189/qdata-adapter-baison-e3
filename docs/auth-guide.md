# 百胜E3 接口测试指南 (Postman / APIPost)

> ✅ 已验证通过的签名算法（参考 PHP BaisonSDK）

## 连接器基本信息

| 项目 | 值 |
|------|-----|
| 平台名称 | 百胜E3 |
| 平台代码 | `baison_e3` |
| API 路径 | `?app_act=api/ec&app_mode=func` |

## 认证信息

| 项目 | 值 |
|------|-----|
| AppKey | 从百胜E3 开放平台应用管理页面获取 |
| AppSecret | 从百胜E3 开放平台应用管理页面获取 |
| 签名算法 | MD5 |
| 协议版本 | `3.0` |

## 通用请求参数

| 参数 | 说明 |
|------|------|
| `serviceType` | API 接口名称，如 `e3oms.base.sd.get` |
| `format` | 响应格式，固定 `json` |
| `key` | AppKey |
| `requestTime` | 时间戳，格式 `yyyyMMddHHmmss`，GMT+8，误差允许 10 分钟 |
| `version` | API 协议版本，固定 `3.0` |
| `sign_method` | 签名算法，固定 `md5` |
| `sign` | 签名结果 |
| `data` | 消息体，JSON 格式化后的字符串 |

## 响应格式

| 字段 | 说明 |
|------|------|
| `status` | `1`=成功，`-1`=失败 |
| `data` | 响应数据 |
| `message` | 操作消息/错误信息 |
| `requestid` | 请求唯一标识 |

---

## 1. 测试地址

请将 `{base_url}` 替换为你的百胜E3 环境地址：

```
GET {base_url}/?app_act=api/ec&app_mode=func
```

> `base_url`、`AppKey`、`AppSecret` 请咨询百胜E3 技术支持或实施人员获取。

## 2. Query 参数

| 参数名 | 值 | 说明 |
|--------|-----|------|
| `app_act` | `api/ec` | 固定值 |
| `app_mode` | `func` | 固定值 |
| `serviceType` | `e3oms.base.sd.get` | API 接口名称 |
| `key` | `你的 AppKey` | AppKey |
| `requestTime` | `20260609130733` | 时间戳(`yyyyMMddHHmmss`) |
| `version` | `3.0` | 协议版本 |
| `data` | `{"pageNo":1,"pageSize":2}` | 业务参数(JSON字符串) |
| `sign` | `...` | 签名结果（MD5小写） |

> ⚠️ **注意**: 请求中**不要**带 `format` 和 `sign_method` 参数，否则签名会失败！

## 3. 签名算法

```
1. 构建参数对象（包含 secret，用于签名）:
   key=APP_KEY
   requestTime=yyyyMMddHHmmss
   secret=APP_SECRET
   version=3.0
   serviceType=API_NAME
   data=JSON_STRING

2. 移除 data 参数

3. 用 http_build_query 编码剩余参数:
   key=xxx&requestTime=xxx&secret=xxx&version=3.0&serviceType=xxx

4. 拼接 "&data=" + 原始 JSON 字符串:
   key=xxx&requestTime=xxx&secret=xxx&version=3.0&serviceType=xxx&data={"pageNo":1,"pageSize":2}

5. 对整个字符串做 MD5，结果转小写

6. 最终请求参数中移除 secret（只参与签名，不发送）
```

**Python 示例:**

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
sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()  # 小写！
```

## 4. Postman 自动签名脚本

复制 `api-docs/postman-pre-request-script.js` 到 Pre-request Script 标签页，或导入 `api-docs/postman-collection.json`。

使用前请在 Postman 环境变量中设置：

| 变量名 | 说明 |
|--------|------|
| `baison_app_key` | 你的 AppKey |
| `baison_app_secret` | 你的 AppSecret |
| `baison_api` | API 接口名称（可选，默认 `e3oms.base.sd.get`） |
| `baison_data` | 请求 data JSON 字符串（可选） |

## 5. 可测试的查询接口

| 接口 | serviceType |
|------|------------|
| 商店列表 | `e3oms.base.sd.get` |
| 商品列表 | `e3oms.goods.list.get` |
| 订单列表 | `e3oms.order.list.get` |
| 会员列表 | `e3oms.base.user.list.get` |
| 渠道列表 | `e3oms.base.qd.get` |
| 仓库列表 | `e3oms.base.cangku.get` |
| 区域列表 | `e3oms.base.region.list.get` |
| 快递列表 | `e3oms.base.shipping.list.get` |

> ⚠️ **只测试查询接口，不要测试写入接口！**

## 6. 测试注意事项

- **仅测试查询接口（GET）**
- **不要测试写入数据的接口（ADD/UPDATE/DELETE）**
- `base_url`、`AppKey`、`AppSecret` 请咨询百胜E3 技术支持或实施人员获取，**不要提交到 Git**
