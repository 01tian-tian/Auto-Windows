"""测试 ModelScope Kimi K2.5 API 连接"""

from openai import OpenAI

print("=" * 50)
print("测试 ModelScope Kimi K2.5 API 连接")
print("=" * 50)

client = OpenAI(
    base_url="https://api-inference.modelscope.cn/v1",
    api_key="ms-9cd95f55-7de6-4af3-b493-15d15b081740",
)

print("\n📡 发送请求到 ModelScope API...")
print("   Base URL: https://api-inference.modelscope.cn/v1")
print("   Model: moonshotai/Kimi-K2.5")
print()

try:
    response = client.chat.completions.create(
        model="moonshotai/Kimi-K2.5",
        messages=[
            {"role": "user", "content": "你好，请简单回复一下。"}
        ],
        max_tokens=50,
    )
    print("✅ 连接成功！")
    print(f"\n📝 模型回复: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ 连接失败！")
    print(f"   错误类型: {type(e).__name__}")
    print(f"   错误信息: {str(e)}")

print("\n" + "=" * 50)
