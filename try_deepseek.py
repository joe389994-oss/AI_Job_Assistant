import os
from openai import OpenAI

# 从环境变量读取 API Key，不要把密钥直接写在代码里
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError("没有读取到 DEEPSEEK_API_KEY，请检查环境变量")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


# 提示词
system_prompt = """
你是一名专业的 AI 招聘顾问。

你的任务是从用户提供的简历和岗位描述中提取技能。

请遵守以下规则：
1. 从岗位描述中提取岗位要求的技能。
2. 从简历中提取用户明确掌握或实践过的技能。
3. 不要编造简历中没有出现的技能。
4. evidence 用于记录简历中能够证明技能的项目或经历。
5. 不要进行技能匹配分析，只负责提取。
6. 必须返回合法的 JSON 对象。
7. JSON 必须包含 required_skills、resume_skills、evidence 三个字段。
8. 三个字段的值都必须是字符串数组。
"""

resume_text = """
我学习过 Python、FastAPI 和 SQLite，
并且独立开发过一个水果库存管理系统。
"""

job_description = """
招聘 AI 应用开发工程师。

要求：
1. 熟悉 Python。
2. 熟悉 FastAPI。
3. 了解 RAG 技术。
4. 有大模型 API 调用经验。
"""

user_prompt = f"""
请分析以下内容：

简历：
{resume_text}

岗位描述：
{job_description}
"""

# 调用大模型
response = client.chat.completions.create(
    model="deepseek-flash",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    response_format={"type": "json_object"},
    max_tokens=300,
    extra_body={"thinking": {"type": "disabled"}}
)

print("模型回复：")
print(response.choices[0].message.content)

print("本次 Token 使用情况：")
print(response.usage)


