#!/usr/bin/env python3
"""
多模态测试脚本

使用方法：
    python scripts/test_multimodal.py
"""
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.llm_service import get_llm_service


def test_multimodal():
    """测试多模态图片分析"""
    print("=" * 50)
    print("PetMind 多模态测试")
    print("=" * 50)

    llm_service = get_llm_service()

    # 测试纯文本对话（验证 API 是否正常）
    print("\n[1/2] 测试文本对话...")
    try:
        result = llm_service.chat_with_prompt(
            system_prompt="你是一个专业的宠物健康顾问。",
            user_prompt="你好，请介绍一下犬瘟热的症状。"
        )
        print(f"文本对话结果：\n{result[:500]}...")
        print("✅ 文本对话测试成功！")
    except Exception as e:
        print(f"❌ 文本对话测试失败：{e}")
        return

    # 测试图片分析（如果有测试图片）
    print("\n[2/2] 测试图片分析...")
    data_dir = Path(__file__).parent.parent / "data"

    # 自动查找测试图片（支持多种格式）
    test_image = None
    for ext in ["png", "jpg", "jpeg", "JPG", "JPEG", "PNG"]:
        candidate = data_dir / f"test_image.{ext}"
        if candidate.exists():
            test_image = candidate
            break

    if not test_image:
        print(f"⚠️ 测试图片不存在，请将图片放到 data/ 目录并命名为 test_image.png 或 test_image.jpg")
        print("支持的格式: png, jpg, jpeg")
        print("\n多模态 API 调用代码已就绪！")
        return

    try:
        print(f"使用测试图片: {test_image}")
        result = llm_service.analyze_image(
            image_path=str(test_image),
            user_prompt="请分析这张图片中的宠物健康状况"
        )
        print(f"图片分析结果：\n{result[:500]}...")
        print("✅ 图片分析测试成功！")
    except Exception as e:
        print(f"❌ 图片分析测试失败：{e}")

    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    test_multimodal()
