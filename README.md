# BaisonE3Adapter

<p align="center">
  <strong>QDataV2 baison-e3 适配器</strong>
</p>

<p align="center">
  由 <a href="https://www.qeasy.cloud">广东轻亿云软件科技有限公司</a> 开发<br>
  「轻易云数据集成平台」官方适配器
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://pypi.org/project/qdata-adapter-baison-e3/"><img src="https://img.shields.io/pypi/v/qdata-adapter-baison-e3.svg" alt="PyPI version"></a>
  <a href="https://github.com/qeasy/qdata-adapter-baison-e3/actions/workflows/ci.yml"><img src="https://github.com/qeasy/qdata-adapter-baison-e3/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
</p>

---

## 🚀 快速开始

查看 [QUICKSTART.md](QUICKSTART.md) 获取 5 分钟上手指南。

```bash
# 安装
pip install qdata-adapter-baison-e3

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API 凭据

# 运行示例
python examples/quickstart.py
```

---

## 📖 简介

`qdata-adapter-baison-e3` 是 QDataV2 数据集成平台的官方适配器，用于连接 **baison-e3** 平台。

---

## 🚀 快速开始

### 安装

```bash
pip install qdata-adapter-baison-e3
```

### 基础用法

```python
import asyncio
from qdata_adapter_baison_e3 import BaisonE3Adapter
from qdata_adapter import ConnectorContext

async def main():
    # 创建连接器上下文
    context = ConnectorContext(
        connector_id="my-connector",
        app_software_code="baison_e3",
        base_url="https://api.example.com",
        auth_config={
            "client_id": "your-client-id",
            "client_secret": "your-client-secret",
        },
    )

    # 初始化适配器
    adapter = BaisonE3Adapter(context)

    # 测试连接
    result = await adapter.test_connection()
    print(f"连接状态: {result.status}")

    # 查询数据
    async for item in adapter.list_objects("orders", page_size=50):
        print(item)

asyncio.run(main())
```

---

## ⚙️ 配置说明

### auth_config 格式

根据接口类型不同，`auth_config` 格式可能不同：

```python
# 示例：OAuth2 认证
{
    "client_id": "应用 Key",
    "client_secret": "应用 Secret",
    "token_url": "https://api.example.com/oauth/token",
}

# 示例：API Key 认证
{
    "api_key": "your-api-key",
    "api_secret": "your-api-secret",
}

# 示例：Session 认证
{
    "username": "用户名",
    "password": "密码",
    "account_id": "账套 ID",
}
```

### settings 配置

```python
{
}
```

---

## 📚 API 文档

### BaisonE3Adapter

适配器主类，继承自 `BaseAppAdapter`。

#### 方法

| 方法 | 说明 |
|------|------|
| `authenticate()` | 获取认证 Token |
| `refresh_token()` | 刷新 Token |
| `list_objects(type, filters, page_size)` | 列表查询（自动翻页） |
| `get_object(type, id)` | 单条查询 |
| `create_object(type, data)` | 创建对象 |
| `test_connection()` | 连接测试 |

---

## 🧪 测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试（Mock 模式）
make test

# 使用真实 API 测试（需配置 .env）
USE_REAL_API=true make test

# 录制 HTTP 流量（用于调试）
RECORD_HTTP_TRAFFIC=true make test

# 运行测试（带覆盖率）
make test-cov

# 代码检查
make check
```

### 测试配置

1. 复制 `.env.example` 为 `.env`
2. 填入真实 API 凭据
3. 运行 `USE_REAL_API=true pytest tests/ -v`

⚠️ **注意**: 真实 API 测试会产生实际调用！

测试数据保存在 `tests/data/recordings/`（已配置为 Git 忽略）

---

## 📄 许可与商业政策
本项目采用 **MIT** 开源协议。

---

## 🏢 关于轻易云数据集成平台

**广东轻亿云软件科技有限公司**  
专注数据集成与处理，提供企业级 ETL/ELT 解决方案  
🌐 官网：[https://www.qeasy.cloud](https://www.qeasy.cloud)  
📧 开源项目：opensource@qeasy.cloud  
📧 商业咨询：vincent@qeasy.cloud

---

*Powered by [广东轻亿云软件科技有限公司](https://www.qeasy.cloud)*