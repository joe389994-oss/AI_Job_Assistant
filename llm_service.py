import os
import json

from openai import OpenAI
from pydantic import ValidationError

from models import SkillExtraction


api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError("没有读取到 DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# prompt 函数
def build_prompts(resume_text, job_description):

    system_prompt = """
    你是一名专业的 AI 招聘顾问。

    你的任务是从简历和岗位描述中提取技能。

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

    user_prompt = f"""
    请分析以下内容：

    简历：
    {resume_text}

    岗位描述：
    {job_description}
    """

    return system_prompt, user_prompt


# 发送prompt 接收json字符串
def call_deepseek(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        max_tokens=500,
        extra_body={"thinking": {"type": "disabled"}}
    )

    return response.choices[0].message.content


# 解析json和pydantic 校验
def parse_extraction(json_text):
    data = json.loads(json_text)

    extraction = SkillExtraction(**data)

    return extraction


# 重试函数

def extract_skills_with_llm(resume_text, job_description):
    system_prompt, user_prompt = build_prompts(
        resume_text,
        job_description
    )

    last_error = None

    for attempt in range(2):
        try:
            # 1. 调用模型
            result = call_deepseek(system_prompt, user_prompt)

            # 2. 解析 JSON 并进行 Pydantic 校验
            extraction = parse_extraction(result)

            # 3. 成功，返回结果
            return extraction

        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e

            print(f"第 {attempt + 1} 次尝试失败：{e}")

            # 4. 如果还有重试机会，反馈错误
            user_prompt += f"""

            你上一次返回的数据没有通过程序校验。

            错误信息：
            {e}

            请修正错误，重新返回符合原有 JSON 结构的数据。
            """

    # 5. 两次都失败
    raise RuntimeError(
        "技能提取失败，已达到最大尝试次数"
    ) from last_error



if __name__ == "__main__":

    system_prompt, user_prompt = build_prompts(
        "我学习过 Python、FastAPI 和 SQLite。",
        "岗位要求 Python、FastAPI、RAG。"
    )

    result = call_deepseek(system_prompt, user_prompt)

    print("模型返回内容：")
    print(result)

    print("返回类型：")
    print(type(result))


    extraction = parse_extraction(result)

    print(extraction)