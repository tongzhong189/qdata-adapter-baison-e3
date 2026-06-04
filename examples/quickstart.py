#!/usr/bin/env python3
"""
BaisonE3Adapter 快速开始示例

运行前请确保：
1. 已安装适配器: pip install -e .
2. 已配置环境变量 (cp .env.example .env 并填写)

或者直接在代码中填入你的 API 凭据（不推荐用于生产）
"""

import asyncio
import os

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from qdata_adapter_baison_e3 import BaisonE3Adapter
from qdata_adapter import ConnectorContext


async def main():
    """主函数"""

    # 从环境变量读取配置（优先）或使用默认值
    base_url = os.getenv("BAISON_E3_BASE_URL", "https://api.example.com")
    client_id = os.getenv("BAISON_E3_CLIENT_ID", "your-client-id")
    client_secret = os.getenv("BAISON_E3_CLIENT_SECRET", "your-client-secret")

    print(f"🔗 连接到: {base_url}")
    print(f"🆔 Client ID: {client_id[:8]}..." if len(client_id) > 8 else f"🆔 Client ID: {client_id}")

    # 创建连接器上下文
    context = ConnectorContext(
        connector_id="quickstart-demo",
        app_software_code="baison_e3",
        base_url=base_url,
        auth_config={
            "client_id": client_id,
            "client_secret": client_secret,
            "token_url": f"{base_url}/oauth/token",
        },
        environment="sandbox",  # 使用沙盒环境测试
    )

    # 初始化适配器
    adapter = BaisonE3Adapter(context)

    try:
        # 1. 测试连接
        print("\n📡 测试连接...")
        result = await adapter.test_connection()

        if result.success:
            print(f"✅ 连接成功! ({result.duration_ms}ms)")
            print(f"   接口: {result.metadata.get('interface', 'unknown')}")
        else:
            print(f"❌ 连接失败: {result.message}")
            return

        # 2. 查询数据示例
        print("\n📋 查询数据示例...")
        print("   获取订单列表（前 5 条）:")

        count = 0
        async for order in adapter.list_objects("orders", page_size=5):
            print(f"   - 订单 {order.get('id', 'N/A')}: {order.get('status', 'unknown')}")
            count += 1
            if count >= 5:
                break

        if count == 0:
            print("   （暂无数据或需要配置真实 API 凭据）")

        # 3. 使用 invoke() 灵活调用
        print("\n🎯 使用 invoke() 灵活调用:")

        # 查询示例
        result = await adapter.invoke(
            method="query",
            object_type="products",
            params={"status": "active", "limit": 3}
        )
        print(f"   查询到 {result.get('total', 0)} 个产品")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n💡 提示:")
        print("   1. 确保已配置正确的 API 凭据（.env 文件）")
        print("   2. 检查网络连接")
        print("   3. 查看 api-docs/ 了解 API 详情")
        raise

    print("\n✨ 示例完成!")
    print("\n下一步:")
    print("   - 查看完整文档: README.md")
    print("   - 了解测试配置: tests/conftest.py")
    print("   - API 参考: api-docs/README.md")


if __name__ == "__main__":
    asyncio.run(main())