# qdata-adapter-baison-e3

<p align="center">
  <strong>QDataV2 百胜E3适配器</strong>
</p>

<p align="center">
  由 <a href="https://www.qeasy.cloud">广东轻亿云软件科技有限公司</a> 开发<br>
  「轻易云数据集成平台」官方适配器
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://pypi.org/project/qdata-adapter-baison-e3/"><img src="https://img.shields.io/pypi/v/qdata-adapter-baison-e3.svg" alt="PyPI version"></a>
</p>

---

## 📖 简介

`qdata-adapter-baison-e3` 是 QDataV2 数据集成平台的官方适配器，用于连接 **百胜E3**（Baison E3）企业管理软件系统。

### 核心能力

- **标准 REST API**: 统一的 RESTful 接口设计
- **多种认证**: 支持 OAuth2、API Key、Session 等认证方式
- **完整 CRUD**: 支持查询、创建、更新、删除操作
- **自动翻页**: 内置翻页处理，支持游标/offset/page 多种策略
- **异步迭代**: 流式读取，内存友好

### 适用场景

- 零售行业 ERP 数据集成
- 供应链管理数据同步
- 电商平台订单流转

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
    context = ConnectorContext(
        connector_id="baison-e3-001",
        app_software_code="baison_e3",
        base_url="https://api.baison-e3.com",
        auth_config={
            "client_id": "应用Key",
            "client_secret": "应用Secret",
            "token_url": "https://api.baison-e3.com/oauth/token",
        },
    )

    adapter = BaisonE3Adapter(context)

    # 测试连接
    result = await adapter.test_connection()
    print(f"连接状态: {result.status}")

    # 查询订单列表
    async for order in adapter.list_objects("orders", page_size=100):
        print(order)

asyncio.run(main())
```

---

## ⚙️ 配置说明

### auth_config 格式

```python
# OAuth2 认证（推荐）
{
    "client_id": "应用Key",
    "client_secret": "应用Secret",
    "token_url": "https://api.baison-e3.com/oauth/token",
}

# API Key 认证
{
    "api_key": "API密钥",
    "api_secret": "API密钥私钥",
}

# Session 认证
{
    "username": "用户名",
    "password": "密码",
    "company_code": "企业代码",
}
```

### settings 配置

```python
{
    "interface": "standard",  # 接口类型，默认 "standard"
    "locale": "zh_CN",        # 本地化，默认 "zh_CN"
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
| `update_object(type, id, data)` | 更新对象 |
| `delete_object(type, id)` | 删除对象 |
| `test_connection()` | 连接测试 |
| `health_check()` | 健康检查 |

---

## 🧪 测试

```bash
# 安装开发依赖
make install-dev

# 运行测试（Mock 模式）
make test

# 运行测试（带覆盖率）
make test-cov

# 代码检查
make check
```

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