#!/usr/bin/env python3
"""
BaisonE3Adapter 快速开始示例

运行前请确保：
1. 已安装适配器: pip install -e .
2. 已配置环境变量 (cp ../.env.example .env 并填写)

或者直接在代码中填入你的 API 凭据（不推荐用于生产）

认证方式：百胜E3 使用 AppKey + AppSecret + MD5 签名认证，不是 OAuth2。
"""

import asyncio
import os

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from qdata_adapter import ConnectorContext
from qdata_adapter_baison_e3 import BaisonE3Adapter


async def main():
    """主函数"""

    # 从环境变量读取配置（优先）或使用示例占位符
    base_url = os.getenv(
        "BAISON_E3_BASE_URL",
        "https://your-baison-e3-domain/webopm/web/",
    )
    app_key = os.getenv("BAISON_E3_APP_KEY", "your-app-key")
    app_secret = os.getenv("BAISON_E3_APP_SECRET", "your-app-secret")

    # 检查是否仍为占位符
    if base_url.endswith("your-baison-e3-domain/webopm/web/"):
        print("⚠️  警告: 你正在使用示例占位符地址。")
        print("    请设置 BAISON_E3_BASE_URL 环境变量，或在 .env 文件中填入真实配置。")
        print("    base_url、AppKey、AppSecret 请咨询百胜E3 技术支持获取。")
        return

    print(f"🔗 连接到: {base_url}")
    print(
        f"🆔 App Key: {app_key[:8]}..."
        if len(app_key) > 8
        else f"🆔 App Key: {app_key}"
    )

    # 创建连接器上下文
    context = ConnectorContext(
        connector_id="quickstart-demo",
        app_software_code="baison_e3",
        base_url=base_url,
        auth_config={
            # 百胜E3 使用 AppKey + AppSecret + MD5 签名
            "app_key": app_key,
            "app_secret": app_secret,
            # 兼容别名：key / secret / client_id / client_secret
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
        print("   获取商店列表（前 5 条）:")

        count = 0
        async for shop in adapter.list_objects("shops", page_size=5):
            print(
                f"   - 商店 {shop.get('khdm', 'N/A')}: "
                f"{shop.get('khmc', 'unknown')}"
            )
            count += 1
            if count >= 5:
                break

        if count == 0:
            print("   （暂无数据或需要配置真实 API 凭据）")

        # 3. 使用 invoke() 灵活调用
        print("\n🎯 使用 invoke() 灵活调用:")

        # 使用内置别名查询商品
        result = await adapter.invoke(
            method="query",
            object_type="products",
            params={"pageNo": 1, "pageSize": 3},
        )
        data = result.get("data", [])
        total = 0
        if data and isinstance(data, list) and isinstance(data[0], dict):
            page_info = data[0].get("page", {})
            if isinstance(page_info, list) and page_info:
                page_info = page_info[0]
            total = (page_info or {}).get("totalResult", 0)
        print(f"   查询到 {total} 个产品")

        # 4. 直接传入 serviceType 调用未内置别名的接口
        print("\n🚀 直接调用 serviceType:")
        result = await adapter.invoke(
            method="query",
            object_type="e3oms.base.region.list.get",
            params={"pageNo": 1, "pageSize": 3},
        )
        print(f"   响应状态: {result.get('status')}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n💡 提示:")
        print("   1. 确保已配置正确的 AppKey / AppSecret（.env 文件）")
        print("   2. 检查 base_url 是否正确")
        print("   3. 检查服务器时间与本地时间误差是否在 10 分钟内")
        print("   4. 查看 api-docs/ 了解 API 详情")
        raise

    print("\n✨ 示例完成!")
    print("\n下一步:")
    print("   - 查看完整文档: README.md")
    print("   - 了解测试配置: tests/conftest.py")
    print("   - API 参考: api-docs/README.md")


if __name__ == "__main__":
    asyncio.run(main())
