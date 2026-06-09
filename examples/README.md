# 示例代码

此目录包含 `qdata-adapter-baison-e3` 适配器的使用示例。

## 文件说明

| 文件 | 说明 |
|------|------|
| `quickstart.py` | 快速开始示例，展示适配器初始化、连接测试、列表查询与 `invoke()` 用法 |

## 运行示例

### 1. 配置环境变量

```bash
# 从项目根目录复制环境变量模板
cp ../.env.example .env

# 编辑 .env 填入你的百胜E3 API 凭据
# 认证方式：AppKey + AppSecret + MD5 签名
```

`.env` 示例：

```bash
BAISON_E3_BASE_URL=https://your-sandbox-domain/webopm/web/
BAISON_E3_APP_KEY=your-app-key
BAISON_E3_APP_SECRET=your-app-secret
BAISON_E3_ENVIRONMENT=sandbox
```

> 注意：
> - 百胜E3 使用 **AppKey + AppSecret + MD5 签名** 认证，不是 OAuth2。请勿使用 `CLIENT_ID` / `CLIENT_SECRET` 配置。
> - `base_url`、`AppKey`、`AppSecret` 请咨询百胜E3 技术支持或实施人员获取，**不要提交到 Git**。

### 2. 运行示例

```bash
# 进入示例目录
cd examples

# 运行快速开始示例
python quickstart.py
```

### 3. 使用真实 API（可选）

如需使用真实 API 测试：

```bash
# 确保 .env 中配置了真实凭据
export USE_REAL_API=true
python quickstart.py
```

> ⚠️ 真实 API 测试**仅会调用查询接口**，不会新增、修改、删除任何数据。

## 示例输出

```
🔗 连接到: https://your-sandbox-domain/webopm/web/
🆔 App Key: your-ap...

📡 测试连接...
✅ 连接成功! (125ms)
   接口: standard

📋 查询数据示例...
   获取商店列表（前 5 条）:
   - 商店 SH001: 商店1
   - 商店 SH002: 商店2

🎯 使用 invoke() 灵活调用:
   查询到 42 个产品

✨ 示例完成!
```

## 编写自己的代码

参考 `quickstart.py` 创建你的应用：

```python
import asyncio
from qdata_adapter_baison_e3 import BaisonE3Adapter
from qdata_adapter import ConnectorContext

async def my_app():
    context = ConnectorContext(
        connector_id="my-connector",
        app_software_code="baison_e3",
        base_url="https://your-baison-e3-domain/webopm/web/",
        auth_config={
            "app_key": "你的 AppKey",
            "app_secret": "你的 AppSecret",
        },
        environment="sandbox",
    )

    adapter = BaisonE3Adapter(context)

    # 测试连接
    result = await adapter.test_connection()
    print(f"连接状态: {result.success} - {result.message}")

    # 遍历订单列表（自动分页）
    async for order in adapter.list_objects("orders", page_size=100):
        print(order)

asyncio.run(my_app())
```

## 更多文档

- [项目 README](../README.md)
- [API 文档](../api-docs/README.md)
- [开发规范](../docs/prompt.md)
- [认证与签名指南](../docs/auth-guide.md)
