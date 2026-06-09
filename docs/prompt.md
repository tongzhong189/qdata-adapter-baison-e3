## 🎯 任务概述

请基于 QDataV2 适配器规范，开发 **baison-e3** 平台的官方适配器。

### 项目基本信息

- **适配器名称**: baison-e3
- **Python 包名**: qdata-adapter-baison-e3
- **主类名**: BaisonE3Adapter
- **模块名**: qdata_adapter_baison_e3
- **接口模式**: 单接口（standard）

---

## 📚 参考资源

### 官方文档

- **官方文档中心**: <https://openapi.baison.net/index.html#/doc>
- **本目录接口清单**: `api-docs/apis_list.json`
- **开发者中心**: 百胜E3 开放平台后台（由客户/实施人员提供账号）

### 本地资源

```
项目根目录/
├── api-docs/                    # API 文档入口
│   ├── README.md
│   ├── apis_list.json           # 139 个接口清单
│   ├── README.md                # 文档入口（含错误码参考）
│   ├── postman-collection.json
│   └── postman-pre-request-script.js
├── docs/                        # 项目文档
│   ├── prompt.md                # 本文件
│   ├── auth-guide.md            # 认证与签名指南
│   └── connector.md             # 连接器基本信息
├── .env.example                 # 环境变量模板
├── src/qdata_adapter_baison_e3/ # 适配器源码目录
└── tests/                       # 测试目录
```

### 关键参考文件

1. **接口清单**: `api-docs/apis_list.json` - 完整的 139 个接口定义和参数
2. **环境配置**: `.env.example` - 测试配置模板
3. **认证与签名**: `docs/auth-guide.md` - 已验证的签名算法
4. **认证与连接**: `docs/auth-guide.md` - 平台代码、认证方式、响应格式

---

## 🏗️ 开发规范

### 1. 架构要求

基于 **qdata-adapter** SDK 开发：

```python
from qdata_adapter import BaseAppAdapter, ConnectorContext

class BaisonE3Adapter(BaseAppAdapter):
    """baison-e3 平台适配器"""

    # 平台标识
    app_code = "baison_e3"

    # 单一接口实现
    INTERFACE_MAP = {
        "standard": BaisonE3AdapterStandardInterface,
    }
```

### 2. 目录结构

必须遵循以下结构：

```
src/qdata_adapter_baison_e3/
├── __init__.py           # 导出主类
├── adapter.py            # 主适配器实现
├── exceptions.py         # 自定义异常
├── interfaces/           # 接口实现
│   ├── __init__.py
│   ├── base.py           # 接口基类
│   └── standard.py       # standard 接口（AppKey + MD5 签名）
└── py.typed
```

### 3. 接口规范

#### 认证方式

百胜E3 使用 **AppKey + AppSecret + MD5 签名** 认证，不是 OAuth2：

```python
auth_config = {
    "app_key": "你的 AppKey",
    "app_secret": "你的 AppSecret",
    # 兼容别名：key / secret / client_id / client_secret
}
```

签名规则（参考 PHP BaisonSDK）：

1. 参数：`key`、`requestTime`、`secret`、`version=3.0`、`serviceType`、`data`
2. 签名时先移除 `data`
3. `urlencode` 编码剩余参数
4. 拼接 `"&data="` + 原始 JSON 字符串
5. MD5，结果转**小写**
6. 最终请求中**不发送** `secret`

#### 请求格式

```
GET {base_url}/?app_act=api/ec&app_mode=func
    &serviceType=e3oms.base.sd.get
    &key=APP_KEY
    &requestTime=yyyyMMddHHmmss
    &version=3.0
    &data=JSON_STRING
    &sign=MD5_LOWERCASE
```

#### 响应格式

```json
{
  "status": 1,
  "message": "success",
  "data": [...],
  "requestid": "xxx"
}
```

- `status == 1` 或 `"api-success"`：成功
- `status == -1` 或其他值：失败
- 错误信息包含"签名"或 `sign`：认证错误
- 错误信息包含"IP" + "授权"：IP 白名单错误

#### 标准方法实现

必须实现以下核心方法：

```python
async def authenticate(self) -> dict:
    """验证 AppKey/AppSecret 是否有效"""

async def test_connection(self) -> TestConnectionResult:
    """测试连接可用性"""

async def list_objects(
    self,
    object_type: str,
    filters: dict | None = None,
    page_size: int = 100
) -> AsyncIterator[dict]:
    """列表查询（自动分页）"""

async def get_object(self, object_type: str, object_id: str) -> dict:
    """单条查询"""

async def create_object(self, object_type: str, data: dict) -> dict:
    """创建对象"""

async def invoke(
    self,
    method: str,
    object_type: str,
    data: dict | None = None,
    params: dict | None = None
) -> dict:
    """灵活调用任意 serviceType"""
```

#### 对象类型别名

适配器内置 `object_type -> serviceType` 映射，支持 `shop`、`goods`、`orders` 等别名。未内置的接口可直接传入完整 `serviceType` 调用 `invoke()`。完整映射表参见 `api-docs/README.md`。

---

## 🧪 测试规范

### 测试原则

1. **只读测试**: 严禁新增、修改、删除数据，仅做查询类操作
2. **双环境验证**: 必须同时支持沙箱环境和生产环境
3. **Mock 优先**: 默认使用 Mock 数据，真实 API 测试需显式开启

### 测试环境配置

复制 `.env.example` 为 `.env`，填入凭据：

```bash
# 沙箱环境
BAISON_E3_BASE_URL=https://your-sandbox-domain/webopm/web/
BAISON_E3_APP_KEY=your-app-key
BAISON_E3_APP_SECRET=your-app-secret
BAISON_E3_ENVIRONMENT=sandbox

# 生产环境（谨慎使用）
# BAISON_E3_BASE_URL=https://your-production-domain/webopm/web/
# BAISON_E3_APP_KEY=your-app-key
# BAISON_E3_APP_SECRET=your-app-secret
```

> `base_url`、`AppKey`、`AppSecret` 请咨询百胜E3 技术支持或实施人员获取，**不要提交到 Git**。

### 测试命令

```bash
# 运行所有测试（Mock 模式）
make test

# 沙箱环境真实 API 测试
USE_REAL_API=true BAISON_E3_ENVIRONMENT=sandbox make test

# 录制 HTTP 流量（用于调试）
RECORD_HTTP_TRAFFIC=true make test

# 代码检查
make check

# 格式化
make format
```

### 测试文件结构

```
tests/
├── conftest.py          # pytest 配置和 fixtures
├── test_adapter.py      # 主适配器测试
└── data/                # 测试数据
    ├── fixtures/        # 静态测试数据
    └── recordings/      # HTTP 录制（gitignore）
```

---

## 📝 开发步骤

### Phase 1: 分析设计

1. 阅读 `api-docs/apis_list.json` 理解接口清单
2. 阅读 `docs/auth-guide.md` 掌握签名算法
3. 阅读 `.env.example` 了解环境配置
4. 设计适配器架构：
    - 认证方式：AppKey + AppSecret + MD5 签名
    - 接口划分：单接口 standard
    - 核心方法映射

### Phase 2: 核心实现

1. **接口层实现**:
    - 实现 `interfaces/base.py` 定义接口基类
    - 实现 `interfaces/standard.py` standard 接口（签名、请求构建、响应解析、分页）

2. **认证层实现**:
    - 在 standard 接口中实现 MD5 签名
    - 通过调用查询接口验证 AppKey/AppSecret 有效性

3. **适配器主类**:
    - 实现 `adapter.py` 主类
    - 实现标准方法（`test_connection`、`list_objects`、`get_object`、`create_object`、`invoke`）

### Phase 3: 测试验证

1. 编写 Mock 测试用例
2. 配置 `.env` 进行沙箱环境测试
3. 验证所有查询类接口
4. 检查代码覆盖率（>80%）

### Phase 4: 文档完善

1. 完善 `README.md` 使用示例
2. 更新 `api-docs/README.md` 接口说明
3. 编写/更新 `examples/quickstart.py` 完整示例
4. 更新 `docs/prompt.md` 开发规范

---

## ⚠️ 重要约束

### 数据安全

- **严禁**: 在测试中创建、修改、删除任何数据
- **严禁**: 将真实凭据提交到 Git
- **必须**: 使用 `.env` 管理敏感配置
- **必须**: 检查 `.gitignore` 已包含 `.env` 和 `tests/data/recordings/`

### 代码质量

- 遵循 PEP8 规范
- 类型注解覆盖率 100%
- 核心方法必须有 docstring
- 使用 `ruff` 和 `black` 格式化代码：`make format`

### 兼容性

- Python 3.11+
- 支持 asyncio 异步调用
- 异常处理必须转换为 qdata-adapter 标准异常

---

## 🔍 验收标准

完成开发后，必须满足：

- [ ] `make test` 所有测试通过（Mock 模式）
- [ ] `make check` 代码检查通过
- [ ] `make format` 格式化无变更
- [ ] 沙箱环境真实 API 测试通过
- [ ] 代码覆盖率 >= 80%
- [ ] `examples/quickstart.py` 可正常运行
- [ ] README 文档完整

---

## 💡 提示

### 从 PHP 迁移的注意事项

1. **数组 vs Dict**: PHP 数组对应 Python dict，注意嵌套结构
2. **JSON 处理**: Python 使用 `json.dumps()` / `json.loads()`，签名时注意 `ensure_ascii=False, separators=(",", ":")`
3. **异步调用**: 必须使用 `async/await`，不可使用同步 HTTP 库
4. **类型注解**: 添加完整的类型提示，特别是接口返回数据
5. **签名细节**: `secret` 只参与签名，不发送到服务端；MD5 结果必须转**小写**

### 常见问题

**Q: 如何处理分页？**
A: 在 `list_objects()` 中使用 `AsyncIterator`，内部读取响应中的 `page` 字段（`pageNo`、`pageSize`、`pageTotal`、`totalResult`）自动翻页。

**Q: Token 过期如何处理？**
A: 百胜E3 没有 Token 机制，而是每次请求带时间戳和 MD5 签名。`authenticate()` 仅用于验证配置有效性。

**Q: 如何调用未在别名表中的接口？**
A: 直接使用 `invoke()` 并传入完整 `serviceType`，例如：

```python
await adapter.invoke(
    "query",
    "e3oms.order.info.through.goods.sn.get",
    params={"goodsSn": "SN001"}
)
```

**Q: 为什么签名失败？**
A: 常见原因：
1. 请求中误带了 `format` 或 `sign_method` 参数
2. MD5 结果没有转小写
3. `data` 字段不是原始 JSON 字符串
4. 时间戳 `requestTime` 与服务器时间误差超过 10 分钟
