#!/usr/bin/env python3
"""测试ScreenMind API的功能"""
import requests
import base64
import io
from PIL import Image, ImageDraw, ImageFont

def create_test_image():
    """创建一个包含简单题目的测试图片"""
    # 创建一个白色背景的图片
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)

    # 添加一个简单的选择题
    try:
        # 使用系统默认字体
        font = ImageFont.load_default()
    except:
        font = None

    # 绘制题目文本
    text_lines = [
        "1. 以下哪个是Python的关键字？",
        "",
        "A. hello",
        "B. def",
        "C. world",
        "D. python"
    ]

    y_position = 50
    for line in text_lines:
        draw.text((50, y_position), line, fill='black', font=font)
        y_position += 40

    # 转换为base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer.getvalue()

def test_analyze_api():
    """测试分析API"""
    print("🧪 开始测试ScreenMind API...")

    # 创建测试图片
    print("📸 创建测试图片...")
    image_data = create_test_image()

    # 准备文件上传
    files = {
        'image': ('test.png', image_data, 'image/png')
    }

    # 调用API
    print("🚀 调用分析API...")
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/analyze',
            files=files,
            timeout=30
        )

        print(f"📡 HTTP状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功!")
            print(f"📝 响应数据: {result}")

            if result.get('success'):
                data = result.get('data', {})
                print("\n🎯 分析结果:")
                print(f"  题目类型: {data.get('question_type', '未知')}")
                print(f"  题目内容: {data.get('question_content', '无')}")
                print(f"  正确答案: {data.get('answer', '无')}")
                print(f"  详细解析: {data.get('explanation', '无')}")
                print(f"  分析耗时: {data.get('analysis_time', 0)}秒")
            else:
                print("❌ 分析失败")
        else:
            print(f"❌ API调用失败")
            try:
                error_data = response.json()
                print(f"🔍 错误详情: {error_data}")
            except:
                print(f"🔍 错误文本: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"🌐 网络错误: {e}")
    except Exception as e:
        print(f"💥 未知错误: {e}")

def test_health_api():
    """测试健康检查API"""
    print("\n💊 测试健康检查API...")
    try:
        response = requests.get('http://localhost:8000/api/v1/health/')
        print(f"📡 健康检查状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ 健康检查通过: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.text}")
    except Exception as e:
        print(f"💥 健康检查错误: {e}")

if __name__ == "__main__":
    test_health_api()
    test_analyze_api()